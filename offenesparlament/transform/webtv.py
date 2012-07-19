from pprint import pprint
import re
import logging
from datetime import datetime
import sys

import sqlaload as sl

from offenesparlament.core import etl_engine
from offenesparlament.core import master_data

log = logging.getLogger(__name__)

def merge_speeches(engine):
    Speech = sl.get_table(engine, 'speech')
    for combo in sl.distinct(engine, Speech, 'wahlperiode', 'sitzung'):
        if combo['sitzung'] != 174:
            continue
        merge_speech(engine, str(combo['wahlperiode']),
                     str(combo['sitzung']))


TOPS = re.compile("(TOP|Tagesordnungspunkte?)\s*(\d{1,3})")
ZPS = re.compile("(ZP|Zusatzpunkte?)\s*(\d{1,3})")


def top_calls(text):
    calls = []
    for name, number in TOPS.findall(text):
        calls.append(('TOP', number))
    for name, number in ZPS.findall(text):
        calls.append(('ZP', number))
    return set(calls)


def match_chair(speech, recd):
    tops = top_calls(speech['text'])
    title = recd['item_label']
    calls = top_calls(title) - set(recd['item_key'].split())
    if len(tops.intersection(calls)) > 0:
        log.debug("TOP --- %s" % title)

def merge_speech(engine, wp, session):
    log.info("Merging media + transcript: %s/%s" % (wp, session))
    WebTV = sl.get_table(engine, 'webtv')
    WebTV_Speeches = sl.get_table(engine, 'webtv_speech')
    changes, recordings = [], []
    for recd in sl.find(engine, WebTV, wp=wp, session=session, 
            order_by='speech_id'):
        recordings.append(recd)
        if not len(changes) or changes[-1] != recd['fingerprint']:
            changes.append(recd)
    #speakers = []
    changes_index = 0

    def emit(speech):
        data = changes[changes_index].copy()
        del data['id']
        data['sequence'] = speech['sequence']
        sl.upsert(engine, WebTV_Speeches, data,
                unique=['wp', 'session', 'sequence'])

    Speech = sl.get_table(engine, 'speech')
    for speech in sl.find(engine, Speech, order_by='sequence', 
        wahlperiode=wp, sitzung=session, matched=True):
        if speech['type'] == 'poi':
            emit(speech)
            continue

        if speech['type'] == 'chair':
            match_chair(speech, changes[changes_index])

        transition = changes[changes_index]
        if len(changes) > changes_index + 1:
            transition = changes[changes_index + 1]

            if speech['fingerprint'] == transition['fingerprint']:
                changes_index += 1
        recd = changes[changes_index]
        #print [speech['fingerprint'], recd['fingerprint'], recd['item_label']]
        emit(speech)


