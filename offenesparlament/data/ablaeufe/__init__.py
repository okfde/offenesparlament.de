import logging

import sqlaload as sl

from offenesparlament.data.lib.db import fetch_row
from offenesparlament.model.indexer import get_indexer
from offenesparlament.data.lib.refresh import Unmodified
from offenesparlament.data.lib.reference import InvalidReference

from offenesparlament.data.ablaeufe.scrape import scrape_index, \
    scrape_ablauf

log = logging.getLogger(__name__)

#TEMP:
def transform():
    """ Transform and clean up content """
    engine = etl_engine()
    from offenesparlament.transform import persons
    #persons.generate_person_long_names(engine)
    from offenesparlament.transform import positions
    #positions.extend_positions(engine)
    from offenesparlament.transform import ablaeufe
    #ablaeufe.extend_ablaeufe(engine)
    from offenesparlament.transform import namematch
    namematch.match_persons(engine)
    persons.generate_person_long_names(engine)
    from offenesparlament.transform import speechparser
    speechparser.load_transcripts(engine)
    from offenesparlament.transform import webtv
    webtv.merge_speeches(engine)
    #from offenesparlament.transform import awatch
    #awatch.load_profiles(engine)
    from offenesparlament.transform import speechmatch
    persons.generate_person_long_names(engine)
    speechmatch.extend_speeches(engine)
    persons.generate_person_long_names(engine)
    from offenesparlament.transform import drs
    drs.merge_speeches(engine)

def process_ablauf(engine, indexer, url, force=False):
    try:
        print url
    except Unmodified: pass

ABLAUF = {
    'generator': scrape_index,
    'handler': process_ablauf
    }

