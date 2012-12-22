import logging

import sqlaload as sl

from offenesparlament.data.lib.threaded import unthreaded
from offenesparlament.data.lib.db import fetch_row
from offenesparlament.model.indexer import get_indexer
from offenesparlament.data.lib.refresh import Unmodified
from offenesparlament.data.lib.reference import InvalidReference

from offenesparlament.data.transcripts.scrape_plpr import scrape_index, \
    scrape_transcript, url_metadata
from offenesparlament.data.transcripts.scrape_webtv import scrape_agenda
from offenesparlament.data.transcripts.resolve import speakers_webtv
from offenesparlament.data.transcripts.merge import merge_speech
from offenesparlament.data.transcripts.load import load_sitzung

log = logging.getLogger(__name__)

def check_done(engine, url, force=False):
    if force:
        return False
    table = sl.get_table(engine, 'speech')
    data = sl.find_one(engine, table, source_url=url, loaded=True)
    return data is not None

def mark_done(engine, url):
    table = sl.get_table(engine, 'speech')
    sl.upsert(engine, table, {
              'loaded': True,
              'source_url': url,
        }, unique=['source_url'])

def process_transcript(engine, indexer, url, force=False):
    try:
        if check_done(engine, url, force=force):
            log.info("%s is done, use -f to force.", url)
            return
        try:
            data = scrape_transcript(engine, url, force=force)
            wp, session = data['wahlperiode'], data['sitzung']
        except Unmodified:
            wp, session = url_metadata(url)
        if not scrape_agenda(engine, wp, session):
            return

        speakers_webtv(engine, wp, session)
        merge_speech(engine, wp, session)
        
        load_sitzung(engine, indexer, wp, session)
        mark_done(engine, url)
    except InvalidReference: pass

def process(engine, indexer, force=False):
    func = lambda url: process_transcript(engine, indexer, url, \
            force=force)
    unthreaded(scrape_index(), func)


