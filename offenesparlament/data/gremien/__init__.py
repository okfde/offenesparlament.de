import logging

from offenesparlament.data.lib.db import fetch_row
from offenesparlament.data.lib.refresh import Unmodified

from offenesparlament.data.gremien.scrape import scrape_index, \
    scrape_gremium
from offenesparlament.data.gremien.load import load_gremium

log = logging.getLogger(__name__)

def process_gremium(engine, indexer, url, force=False):
    try:
        data = scrape_gremium(engine, url, force=force)

        data = fetch_row(engine, 'gremium', key=data['key'])
        gremium = load_gremium(engine, data)
        indexer.add(gremium)
    except Unmodified: pass

GREMIUM = {
    'generator': scrape_index,
    'handler': process_gremium
    }

