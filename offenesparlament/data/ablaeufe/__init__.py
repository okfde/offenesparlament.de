import logging

import sqlaload as sl

from offenesparlament.data.lib.db import fetch_row
from offenesparlament.data.lib.refresh import Unmodified
from offenesparlament.data.lib.reference import InvalidReference

from offenesparlament.data.ablaeufe.scrape import scrape_index, \
    scrape_ablauf, NoContentException
from offenesparlament.data.ablaeufe.clean_positions import \
    extend_positions
from offenesparlament.data.ablaeufe.clean_ablauf import clean_ablauf
from offenesparlament.data.ablaeufe.clean_beitraege import \
    match_beitraege
from offenesparlament.data.ablaeufe.load import load_ablauf

log = logging.getLogger(__name__)

def process_ablauf(engine, indexer, url, force=False):
    try:
        data = scrape_ablauf(engine, url, force=force)
        clean_ablauf(engine, data)
        extend_positions(engine, url)
        match_beitraege(engine, url)

        data = fetch_row(engine, 'ablauf', source_url=url)
        load_ablauf(engine, indexer, data)
    except Unmodified: pass
    except NoContentException: pass

    #import objgraph
    #import random
    #import inspect
    #objgraph.show_growth()
    #objgraph.show_chain(
    #    objgraph.find_backref_chain(
    #        random.choice(objgraph.by_type('dict')),
    #        inspect.ismodule),
    #    filename='chain.png')

ABLAUF = {
    'generator': scrape_index,
    'handler': process_ablauf
    }

