import logging

import sqlaload as sl

from offenesparlament.data.lib.db import fetch_row
from offenesparlament.model.indexer import get_indexer
from offenesparlament.data.lib.refresh import Unmodified
from offenesparlament.data.lib.reference import InvalidReference

from offenesparlament.data.ablaeufe.scrape import scrape_index, \
    scrape_ablauf
from offenesparlament.data.ablaeufe.clean_positions import \
    extend_positions
from offenesparlament.data.ablaeufe.clean_ablauf import clean_ablauf
from offenesparlament.data.ablaeufe.clean_beitraege import \
    match_beitraege

log = logging.getLogger(__name__)


def process_ablauf(engine, indexer, url, force=False):
    try:
        print url
        data = scrape_ablauf(engine, url, force=force)
        clean_ablauf(engine, data)
        extend_positions(engine, url)
        match_beitraege(engine, url)
        print data
    except Unmodified: pass

ABLAUF = {
    'generator': scrape_index,
    'handler': process_ablauf
    }

