from pprint import pprint
import re
import logging
from datetime import datetime
import sys

from offenesparlament.core import master_data

from webstore.client import URL as WebStore

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.NOTSET)

def extend_speeches(db, master):
    Speech = db['mediathek']
    log.info("Post-processing speeches from mediathek...")
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
    
        #pprint(speech)
        #print "Speaker", speech['speech_title'].encode('utf-8')
        Speech.writerow(speech, unique_columns=['speech_source_url'])

QUERY = '''SELECT DISTINCT wahlperiode, sitzung FROM speech;'''

def merge_speeches(db, master):
    for combo in db.query(QUERY):
        merge_speech(db, master, combo['wahlperiode'], 
                combo['sitzung'])


TOPS = re.compile("(TOP|Tagesordnungspunkte?)\s*(\d{1,3})")
ZPS = re.compile("(ZP|Zusatzpunkte?)\s*(\d{1,3})")

def top_calls(text):
    calls = []
    for name, number in TOPS.findall(text):
        calls.append(('TOP', number))
    for name, number in ZPS.findall(text):
        calls.append(('ZP', number))
    return set(calls)

def merge_speech(db, master, wp, session):
    log.info("Merging media + transcript: %s/%s" % (wp, session))
    SpeechMediathek = db['speech_mediathek']
    sorter = lambda x: (int(x['top_nr']), int(x['speech_nr']))
    med = sorted(db['mediathek'].traverse(wahlperiode=wp, meeting_nr=session),
            key=sorter)

    speech_idx = top_idx = 0
    if not len(med):
        return

    def med_fp(idx):
        return med[idx]['fingerprint']
    
    def emit(speech, idx):
        #x = "%s: %s- %s (%s)" % (
        #    med[idx]['speech_source_url'].ljust(30, ' '),
        #    speech['fingerprint'].ljust(45, ' '),
        #    med[idx]['fingerprint'].ljust(45, ' '),
        #    med[idx]['speech_duration'],
        #    )
        #print x.encode("utf-8")
        SpeechMediathek.writerow({
                'wahlperiode': wp,
                'sitzung': session,
                'mediathek_url': med[idx]['speech_source_url'],
                'sequence': speech['sequence']
                }, unique_columns=['wahlperiode', 'sitzung', 'sequence'])

    spch = []
    for speech in db['speech'].traverse(wahlperiode=wp, sitzung=session):
        spch_i = (speech['wahlperiode'], speech['sitzung'], speech['sequence'])
        if spch_i in spch:
            #print "FAIL", speech
            continue
            #return
        spch.append(spch_i)

        if speech['type'] == 'poi':
            emit(speech, speech_idx)
            continue

        if speech['type'] == 'chair':
            tops = top_calls(speech['text'])
            if len(tops):
                #print tops
                j = int(top_idx)
                last_title = 'xxx'
                while True:
                    j += 1
                    if j >= len(med):
                        break
                    title = med[j]['top_title']
                    if last_title == title:
                        continue
                    calls = top_calls(title) - top_calls(med[top_idx]['top_title'])
                    #print tops, med[j]['top_title'].encode("utf-8"), top_calls(med[j]['top_title'])
                    if len(tops.intersection(calls)) > 0:
                        log.debug("TOP --- %s" % title)
                        #pprint({
                        #        "text": len(speech['text']),
                        #        "text_tops": tops,
                        #        "top_tops": top_calls(title),
                        #        "top": med[j]['top_title']
                        #    })
                        speech_idx = top_idx = j
                        break
                    last_title = title
                #print tops
                #print "FOO"
        
        speech_fp = speech['fingerprint']
        # cases: 
        while True:
            if speech_fp == med_fp(speech_idx):
                emit(speech, speech_idx)
                #print med_fp(i+1).encode('utf-8')
                if speech_fp == med_fp(speech_idx+1):
                    # 2. curren matches, next also matches
                    # -> use current and increment
                    speech_idx += 1
                else:
                    # 1. current matches, next does not match
                    # -> use current
                    break
            else:
                if speech_fp == med_fp(speech_idx+1):
                    # 4. current does not match, next matches
                    # -> use next
                    speech_idx += 1
                    emit(speech, speech_idx)
                    break
                else:
                    # 3. current does not match, next does not match
                    # -> use current
                    emit(speech, speech_idx)
                    break


if __name__ == '__main__':
    assert len(sys.argv)==2, "Need argument: webstore-url!"
    db, _ = WebStore(sys.argv[1])
    print "DESTINATION", db
    extend_speeches(db, master_data())
    merge_speech(db, master_data(), 17, 121)
