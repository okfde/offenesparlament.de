import logging

from offenesparlament.data.lib.threaded import unthreaded
from offenesparlament.data.lib.db import fetch_row
from offenesparlament.model.indexer import get_indexer
from offenesparlament.data.lib.refresh import Unmodified
from offenesparlament.data.lib.reference import InvalidReference

from offenesparlament.data.transcripts.scrape_plpr import scrape_index, \
    scrape_transcript, url_metadata
from offenesparlament.data.transcripts.scrape_webtv import scrape_agenda
#from offenesparlament.data.gremien.load import load_gremium

log = logging.getLogger(__name__)


def process_transcript(engine, indexer, url, force=False):
    try:
        try:
            data = scrape_transcript(engine, url, force=force)
            wp, session = data['wahlperiode'], data['sitzung']
        except Unmodified:
            wp, session = url_metadata(url)
        if not scrape_agenda(engine, wp, session):
            return
        print url
        #data = scrape_gremium(engine, url, force=force)

        #data = fetch_row(engine, 'gremium', key=data['key'])
        #gremium = load_gremium(engine, data)
        #indexer.add(gremium)
    except InvalidReference: pass

def process(engine, indexer, force=False):
    func = lambda url: process_transcript(engine, indexer, url, \
            force=force)
    unthreaded(scrape_index(), func)


