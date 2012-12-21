import logging

from offenesparlament.data.lib.threaded import unthreaded
from offenesparlament.data.lib.db import fetch_row
from offenesparlament.model.indexer import get_indexer
from offenesparlament.data.lib.refresh import Unmodified

from offenesparlament.data.persons.scrape import scrape_index, scrape_mdb
from offenesparlament.data.persons.resolve import make_fingerprint
from offenesparlament.data.persons.load import load_person


log = logging.getLogger(__name__)

def process_person(engine, indexer, url, force=False):
    try:
        data = scrape_mdb(engine, url, force=force)
        make_fingerprint(engine, data)

        data = fetch_row(engine, 'person', mdb_id=data['mdb_id'])
        person = load_person(engine, data)
        indexer.add(person)
    except Unmodified: pass

def process(engine, indexer, force=False):
    func = lambda url: process_person(engine, indexer, url, \
            force=force)
    unthreaded(scrape_index(), func)




