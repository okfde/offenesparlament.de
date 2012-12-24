import logging

import sqlaload as sl

from offenesparlament.data.lib.text import url_slug
from offenesparlament.data.lib.persons import make_long_name
from offenesparlament.data.lib.reference import resolve_person, \
    BadReference

log = logging.getLogger(__name__)

def make_fingerprint(engine, person):
    try:
        long_name = make_long_name(person)
        long_name = resolve_person(long_name)
        log.info(" -> %s" % long_name.strip())
        Person = sl.get_table(engine, 'person')
        sl.upsert(engine, Person, {
            'fingerprint': long_name,
            'slug': url_slug(long_name),
            'mdb_id': person['mdb_id']
            }, unique=['mdb_id'])
        Rolle = sl.get_table(engine, 'rolle')
        sl.upsert(engine, Rolle, {
            'mdb_id': person['mdb_id'],
            'fingerprint': long_name
            }, unique=['mdb_id'])
        person['fingerprint'] = long_name
    except BadReference:
        pass

