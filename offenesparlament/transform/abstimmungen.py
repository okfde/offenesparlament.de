import sys
import logging
from pprint import pprint

import sqlaload as sl

from offenesparlament.core import etl_engine
from offenesparlament.core import master_data
from offenesparlament.transform.namematch import match_speaker, make_prints

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.NOTSET)

def extend_abstimmungen(engine, master):
    log.info("Amending votes ...")
    Abstimmung = sl.get_table(engine, 'abstimmung')
    prints = make_prints(engine)
    for data in sl.distinct(engine, Abstimmung, 'person'):
        try:
            fp = match_speaker(master, data['person'], prints)
            if fp is not None:
                sl.upsert(engine, Abstimmung, 
                          {'person': data.get('person'),
                           'fingerprint': fp}, 
                        unique=['person'])
        except ValueError, ve:
            log.exception(ve)

if __name__ == '__main__':
    engine = etl_engine()
    print "DESTINATION", engine
    extend_abstimmungen(engine, master_data())
