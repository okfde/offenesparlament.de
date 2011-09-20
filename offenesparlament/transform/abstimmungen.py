import sys
import logging

from webstore.client import URL as WebStore

from offenesparlament.core import master_data
from offenesparlament.transform.namematch import match_speaker, make_prints

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.NOTSET)

def extend_abstimmungen(db, master):
    log.info("Amending votes ...")
    Abstimmung = db['abstimmung']
    prints = make_prints(db)
    for data in Abstimmung.distinct('person'):
        fp = match_speaker(master, data['person'], prints)
        Abstimmung.writerow({'person': data.get('person'),
                             'fingerprint': fp}, 
                            unique_columns=['person'],
                            bufferlen=2000)
    Abstimmung.flush()

if __name__ == '__main__':
    assert len(sys.argv)==2, "Need argument: webstore-url!"
    db, _ = WebStore(sys.argv[1])
    print "DESTINATION", db
    extend_abstimmungen(db, master_data())
