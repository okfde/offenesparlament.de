#coding: utf-8
import sys
import logging

from nkclient import NKNoMatch, NKInvalid
import sqlaload as sl

from offenesparlament.transform.persons import make_person, make_long_name
from offenesparlament.core import etl_engine, nk_persons

log = logging.getLogger(__name__)

def ensure_rolle(beitrag, fp, engine):
    rolle = {
        'fingerprint': fp,
        'ressort': beitrag.get('ressort'),
        'fraktion': beitrag.get('fraktion'),
        'funktion': beitrag.get('funktion')
        }
    Rolle = sl.get_table(engine, 'rolle')
    sl.upsert(engine, Rolle, rolle,
            unique=['fingerprint', 'funktion'])

def match_beitrag(engine, beitrag):
    nkp = nk_persons()
    beitrag_print = make_long_name(beitrag)
    log.info("Matching: %s", beitrag_print)
    try:
        value = match_speaker(beitrag_print)
        if sl.find_one(engine, sl.get_table(engine, 'person'),
                fingerprint=value) is None:
            make_person(beitrag, value, engine)
        return value
    except NKNoMatch, nm:
        log.info("Beitrag person is unknown: %s", beitrag_print)
        return None
    except NKInvalid, inv:
        log.error("Beitrag person is invalid: %s", beitrag_print)
        return None

def speaker_name_transform(name):
    cparts = name.split(',')
    if '(' in cparts[1]:
        cparts[1], pf = cparts[1].split(' (', 1)
        pf = pf.replace(')', '')
        cparts.append(pf)
    cparts[0], cparts[1] = cparts[1], cparts[0]
    fragment = " ".join(cparts)
    fragment.replace('(', '').replace(')', '')
    return fragment

_SPEAKER_CACHE = {}

def match_speaker(speaker):
    nkp = nk_persons()
    if speaker not in _SPEAKER_CACHE:
        try:
            obj = nkp.lookup(speaker)
        except NKInvalid, inv:
            obj = inv
        except NKNoMatch, nm:
            obj = nm
        _SPEAKER_CACHE[speaker] = obj
    obj = _SPEAKER_CACHE[speaker]
    if isinstance(obj, (NKInvalid, NKNoMatch)):
        raise obj
    return obj.value

def match_speakers_webtv(engine):
    WebTV = sl.get_table(engine, 'webtv')
    for i, speech in enumerate(sl.distinct(engine, WebTV, 'speaker')):
        if speech['speaker'] is None:
            continue
        speaker = speaker_name_transform(speech['speaker'])
        matched = True
        try:
            fp = match_speaker(speaker)
        except NKInvalid, inv:
            fp = None
        except NKNoMatch, nm:
            fp = None
            matched = False
        sl.upsert(engine, WebTV, {'fingerprint': fp,
                                  'matched': matched,
                                  'speaker': speech['speaker']},
                    unique=['speaker'])


def match_beitraege(engine):
    Beitrag = sl.get_table(engine, 'beitrag')
    for i, beitrag in enumerate(sl.distinct(engine, Beitrag, 'vorname',
        'nachname', 'funktion', 'land', 'fraktion', 'ressort', 'ort')):
        if i % 1000 == 0:
            sys.stdout.write('.')
            sys.stdout.flush()
        match = match_beitrag(engine, beitrag)
        ensure_rolle(beitrag, match, engine)
        beitrag['fingerprint'] = match
        beitrag['matched'] = match is not None
        sl.upsert(engine, Beitrag, beitrag, unique=['vorname', 'nachname',
            'funktion', 'land', 'fraktion', 'ressort', 'ort'])


def match_persons(db):
    match_beitraege(db)
    match_speakers_webtv(db)

if __name__ == '__main__':
    engine = etl_engine()
    print "DESTINATION", engine
    match_persons(engine)
