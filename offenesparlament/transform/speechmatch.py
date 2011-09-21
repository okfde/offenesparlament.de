import re
import sys
import logging

from webstore.client import URL as WebStore

from offenesparlament.core import master_data

DRS_MATCH = "- Drucksachen? (%s/\\d{1,6})([,;/]? (%s/\\d{1,6}))* -"

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.NOTSET)

UNIQUE = ['__id__']

def extend_speeches(db, master, wahlperiode=17):
    log.info("Amending speeches with DRS ...")
    drs_match = re.compile(DRS_MATCH % (wahlperiode, wahlperiode))
    Speech = db['speech']
    SpeechDocument = db['speech_document']
    for i, data in enumerate(Speech):
        if data.get('type') != 'chair':
            continue
        if i % 1000 == 0:
            sys.stdout.write('.')
            sys.stdout.flush()
        m = drs_match.search(data.get('text'))
        if m is None:
            continue
        for i, grp in enumerate(m.groups()):
            if grp and '/' in grp:
                wp, nummer = grp.split('/', 1)
                SpeechDocument.writerow({
                    'group': i,
                    'sequence': data['sequence'],
                    'sitzung': data['sitzung'],
                    'wahlperiode': wahlperiode,
                    'dok_nummer': nummer},
                    unique_columns=['sequence', 'sitzung', 'wahlperiode',
                        'group'],
                    bufferlen=5000)
    SpeechDocument.flush()

if __name__ == '__main__':
    assert len(sys.argv)==2, "Need argument: webstore-url!"
    db, _ = WebStore(sys.argv[1])
    print "DESTINATION", db
    extend_speeches(db, master_data())

