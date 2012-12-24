import logging

from offenesparlament.data.lib.db import fetch_row
from offenesparlament.data.lib.refresh import Unmodified
from offenesparlament.data.persons.scrape import scrape_index, scrape_mdb
from offenesparlament.data.persons.resolve import make_fingerprint
from offenesparlament.data.persons.load import load_person
from offenesparlament.data.persons.clean_angaben import parse_angaben

log = logging.getLogger(__name__)

def process_person(engine, indexer, url, force=False):
    try:
        data = scrape_mdb(engine, url, force=force)
        make_fingerprint(engine, data)
        parse_angaben(engine, data)

        data = fetch_row(engine, 'person', mdb_id=data['mdb_id'])
        person = load_person(engine, data)
        indexer.add(person)
    except Unmodified: pass

PERSON = {
    'generator': scrape_index,
    'handler': process_person
    }



