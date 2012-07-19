import sys
import logging
from pprint import pprint

import sqlaload as sl
from nkclient import NKNoMatch, NKInvalid

from offenesparlament.core import etl_engine
from offenesparlament.core import master_data
from offenesparlament.transform.namematch import match_speaker

log = logging.getLogger(__name__)

def extend_abstimmungen(engine):
    log.info("Amending votes ...")
    Abstimmung = sl.get_table(engine, 'abstimmung')
    for data in sl.distinct(engine, Abstimmung, 'person'):
        try:
            fp = match_speaker(data['person'])
        except NKInvalid, inv:
            log.exception(ve)
            continue
        except NKNoMatch, nm:
            fp = None
            log.info("No match for: %s", data['person'])
        sl.upsert(engine, Abstimmung,
                  {'person': data.get('person'),
                   'matched': fp is not None,
                   'fingerprint': fp},
                  unique=['person'])

if __name__ == '__main__':
    engine = etl_engine()
    print "DESTINATION", engine
    extend_abstimmungen(engine)
