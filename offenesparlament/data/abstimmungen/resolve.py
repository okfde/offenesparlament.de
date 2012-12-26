import logging

import sqlaload as sl

from offenesparlament.core import etl_engine
from offenesparlament.data.lib.reference import resolve_person, \
    resolve_votes, BadReference

log = logging.getLogger(__name__)

def resolve_stimmen(engine, source_url):
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

def resolve_abstimmung(engine, source_url):
    table = sl.get_table(engine, 'abstimmung')
    data = sl.find_one(engine, table, source_url=source_url)
    if data is None:
        log.error("No data: %s", source_url)
        return
    subject = data['subject']
    try:
        title = resolve_votes(subject)
    except BadReference:
        title = None
        log.info("No match for: %s", data['person'])
    sl.upsert(engine, table,
              {'subject': subject,
               'title': title},
              unique=['subject'])

    



