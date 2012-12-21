#coding: utf-8
import sys
import logging

import sqlaload as sl

from offenesparlament.transform.persons import make_person, make_long_name
from offenesparlament.data.lib.reference import resolve_person, \
    BadReference, InvalidReference

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
    beitrag_print = make_long_name(beitrag)
    log.info("Matching: %s", beitrag_print)
    try:
        value = resolve_person(beitrag_print)
        if sl.find_one(engine, sl.get_table(engine, 'person'),
                fingerprint=value) is None:
            make_person(beitrag, value, engine)
        return value
    except BadReference:
        log.info("Beitrag person is unknown: %s", beitrag_print)
        return None


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

