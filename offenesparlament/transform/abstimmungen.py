import logging
from pprint import pprint

import sqlaload as sl

from offenesparlament.core import etl_engine
from offenesparlament.data.lib.reference import resolve_person, \
    BadReference

log = logging.getLogger(__name__)

def extend_abstimmungen(engine):
    log.info("Amending votes ...")
    Abstimmung = sl.get_table(engine, 'abstimmung')
    for data in sl.distinct(engine, Abstimmung, 'person'):
        try:
            fp = resolve_person(data['person'])
        except BadReference:
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
