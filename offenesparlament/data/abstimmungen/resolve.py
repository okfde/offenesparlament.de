import logging

import sqlaload as sl

from offenesparlament.core import etl_engine
from offenesparlament.data.lib.reference import resolve_person, \
    BadReference

log = logging.getLogger(__name__)

def resolve_abstimmung(engine, source_url):
    table = sl.get_table(engine, 'abstimmung')
    for data in sl.find(engine, table, source_url=source_url):
        try:
            fp = resolve_person(data['person'])
        except BadReference:
            fp = None
            log.info("No match for: %s", data['person'])
        sl.upsert(engine, table,
                  {'person': data.get('person'),
                   'matched': fp is not None,
                   'fingerprint': fp},
                  unique=['person'])

