from pprint import pprint
import re
import logging
from datetime import datetime
import sys

import sqlaload as sl

from offenesparlament.core import etl_engine
from offenesparlament.core import master_data

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.NOTSET)


def merge_speeches(engine, master):
    Speech = sl.get_table(engine, 'speech')
    for combo in sl.distinct(engine, Speech, 'wahlperiode', 'sitzung'):
        merge_speech(engine, master, str(combo['wahlperiode']),
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

    #if len(tops):
    #    j = int(top_idx)
    #    last_title = 'xxx'
    #    while True:
    #        j += 1
    #        if j >= len(med):
    #            break
    #        title = med[j]['item_key']
    #        if last_title == title:
    #            continue
    #        #print top_calls(title), set(med[top_idx]['item_key'].split())
    #        calls = top_calls(title) - set(med[top_idx]['item_key'].split())
    #        if len(tops.intersection(calls)) > 0:
    #            log.debug("TOP --- %s" % title)
    #            speech_idx = top_idx = j
    #            break
    #        last_title = title
    #    #print tops

def merge_speech(engine, master, wp, session):
    log.info("Merging media + transcript: %s/%s" % (wp, session))
    WebTV = sl.get_table(engine, 'webtv')
    WebTV_Speeches = sl.get_table(engine, 'webtv_speech')
    changes, recordings = [], []
    for recd in sl.find(engine, WebTV, wp=wp, session=session, order_by='speech_id'):
        recordings.append(recd)
        if not len(changes) or changes[-1] != recd['fingerprint']:
            changes.append(recd)
    #speakers = []
    changes_index = 0

    def emit(speech):
        data = changes[changes_index].copy()
        del data['id']
        data['sequence'] = speech['sequence']
        sl.upsert(engine, WebTV_Speeches, data, unique=['wp', 'session', 'sequence'])

    Speech = sl.get_table(engine, 'speech')
    for speech in sl.find(engine, Speech, order_by='sequence', wahlperiode=wp, sitzung=session):
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


def _merge_speech(engine, master, wp, session):
    log.info("Merging media + transcript: %s/%s" % (wp, session))
    SpeechLinks = sl.get_table(engine, 'speech_agenda')
    WebTV = sl.get_table(engine, 'webtv')
    Speech = sl.get_table(engine, 'speech')
    sorter = lambda x: int(x['speech_id'])
    med = sorted(sl.find(engine, WebTV, wp=wp, session=session), key=sorter)

    speech_idx = top_idx = 0
    if not len(med):
        log.error("No mediathek entries: %s/%s", wp, session)
        return

    def med_fp(idx):
        if idx >= len(med):
            return ""
        return med[idx]['fingerprint']

    def emit(speech, idx):
        #x = "%s: %s- %s (%s)" % (
        #    med[idx]['speech_source_url'].ljust(30, ' '),
        #    speech['fingerprint'].ljust(45, ' '),
        #    med[idx]['fingerprint'].ljust(45, ' '),
        #    med[idx]['speech_duration'],
        #    )
        #print x.encode("utf-8")
        sl.upsert(engine, SpeechLinks, {
                'wahlperiode': wp,
                'sitzung': session,
                'mediathek_url': med[idx]['speech_id'],
                'sequence': speech['sequence']
                }, unique=['wahlperiode', 'sitzung', 'sequence'])

    spch = []
    for speech in sl.find(engine, Speech, order_by='sequence', wahlperiode=wp, sitzung=session):
        spch_i = (speech['wahlperiode'], speech['sitzung'], speech['sequence'])
        if spch_i in spch:
            continue
        spch.append(spch_i)
        #print spch_i

        if not speech['fingerprint']:
            continue

        if speech['type'] == 'poi':
            emit(speech, speech_idx)
            continue

        if speech['type'] == 'chair':
            tops = top_calls(speech['text'])
            if len(tops):
                j = int(top_idx)
                last_title = 'xxx'
                while True:
                    j += 1
                    if j >= len(med):
                        break
                    title = med[j]['item_key']
                    if last_title == title:
                        continue
                    #print top_calls(title), set(med[top_idx]['item_key'].split())
                    calls = top_calls(title) - set(med[top_idx]['item_key'].split())
                    if len(tops.intersection(calls)) > 0:
                        log.debug("TOP --- %s" % title)
                        speech_idx = top_idx = j
                        break
                    last_title = title
                #print tops

        speech_fp = speech['fingerprint']

        # cases:
        while True:
            if speech_fp == med_fp(speech_idx):
                emit(speech, speech_idx)
                if speech_fp == med_fp(speech_idx + 1):
                    # 2. curren matches, next also matches
                    # -> use current and increment
                    speech_idx += 1
                else:
                    # 1. current matches, next does not match
                    # -> use current
                    break
            else:
                if speech_fp == med_fp(speech_idx + 1):
                    # 4. current does not match, next matches
                    # -> use next
                    speech_idx += 1
                    emit(speech, speech_idx)
                    break
                else:
                    # 3. current does not match, next does not match
                    # -> use current
                    emit(speech, speech_idx)
                    break
