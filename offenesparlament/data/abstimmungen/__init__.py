import logging

from offenesparlament.data.lib.refresh import Unmodified
from offenesparlament.data.abstimmungen.scrape import scrape_index, \
    scrape_abstimmung
from offenesparlament.data.abstimmungen.resolve import resolve_abstimmung
from offenesparlament.data.abstimmungen.load import load_abstimmung

log = logging.getLogger(__name__)

def process_abstimmung(engine, indexer, url, force=False):
    try:
        data = scrape_abstimmung(engine, url, force=force)
        resolve_abstimmung(engine, data['source_url'])
        load_abstimmung(engine, data['source_url'])
    except Unmodified: pass

ABSTIMMUNG = {
    'generator': scrape_index,
    'handler': process_abstimmung
    }


