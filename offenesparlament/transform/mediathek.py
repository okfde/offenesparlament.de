from pprint import pprint
import logging
from datetime import datetime
import sys

from offenesparlament.core import master_data

from webstore.client import URL as WebStore

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.NOTSET)

def extend_speeches(db, master):
    Speech = db['mediathek']
    for speech in Speech:
        for k, v in speech.items():
            if not k.endswith('pdf_url') or v is None:
                continue
            parts = v.split('#P.')
            if len(parts) > 1:
                url, fragment = parts
            else:
                url = v
                fragment = ''
            speech[k + '_plain'] = url
            speech[k + '_pages'] = fragment
        ctx = speech['speech_context']
        if ctx is not None:
            speech['meeting_nr'], text = ctx.split('.', 1)
            text, date = ctx.rsplit('vom ', 1)
            date = datetime.strptime(date, "%d.%m.%Y")
            speech['meeting_date'] = date.isoformat()
        ctx = speech['meeting_context']
        if ctx is not None:
            speech['wahlperiode'], text = ctx.split('.', 1)
    
        if speech['speech_title']:
            print "Speaker", speech['speech_title'].encode('utf-8')
        Speech.writerow(speech, unique_columns=['speech_source_url'])
        #pprint(speech)

QUERY = '''SELECT DISTINCT wahlperiode, sitzung FROM speech;'''

def merge_speeches(db, master):
    for combo in db.query(QUERY):
        merge_speech(db, master, combo['wahlperiode'], 
                combo['sitzung'])

UNIQUES = ['wahlperiode', 'sitzung', 'sequence', 'mediathek_url']

def merge_speech(db, master, wp, session):
    log.info("Merging media + transcript: %s/%s" % (wp, session))
    Mediathek = db['mediathek']
    Speech = db['speech']
    SpeechMediathek = db['speech_mediathek']
    med = list(Mediathek.traverse(wahlperiode=wp, meeting_nr=session))
    med = sorted(med, key=lambda x: x.get('speech_time'))
    #last_match, i, match = None, 0, None
    i = 0
    if not len(med):
        return
    for speech in Speech.traverse(wahlperiode=wp, sitzung=session):
        #if speech['type'] == 'poi': 
        #    continue
        print speech['fingerprint'].encode('utf-8') if speech['fingerprint'] else ''
        #match = None if not len(med) < i else match
        while True:
            SpeechMediathek.writerow({
                'wahlperiode': wp,
                'sitzung': session,
                'mediathek_url': med[i]['speech_source_url'],
                'sequence': speech['sequence']
                }, unique_columns=UNIQUES)
            if speech['fingerprint'] != med[i]['fingerprint']:
                break
            if len(med) > i:
                i += 1
            else:
                break


if __name__ == '__main__':
    assert len(sys.argv)==2, "Need argument: webstore-url!"
    db, _ = WebStore(sys.argv[1])
    print "DESTINATION", db
    #extend_speeches(db, master_data())
    merge_speech(db, master_data(), 17, 121)
