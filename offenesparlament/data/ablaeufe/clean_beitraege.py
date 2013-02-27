#coding: utf-8
import sys
import logging

import sqlaload as sl

from offenesparlament.data.lib.persons import make_person, make_long_name
from offenesparlament.data.lib.reference import resolve_person, \
    BadReference, InvalidReference

KEYS = ['vorname', 'nachname', 'funktion', 'land',
        'fraktion', 'ressort', 'ort']
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


def match_beitrag(engine, beitrag, url):
    beitrag_print = make_long_name(beitrag)
    log.info("Matching: %s", beitrag_print.encode('ascii', 'replace'))
    try:
        value = resolve_person(beitrag_print)
        if sl.find_one(engine, sl.get_table(engine, 'person'),
                fingerprint=value) is None:
            make_person(engine, beitrag, value, url)
        return value
    except BadReference:
        log.info("Beitrag person is unknown: %s",
                beitrag_print.encode('ascii', 'replace'))


def match_beitraege(engine, url):
    table = sl.get_table(engine, 'beitrag')
    for beitrag in sl.distinct(engine, table, *KEYS, source_url=url):
        match = match_beitrag(engine, beitrag, url)
        beitrag['fingerprint'] = match
        beitrag['matched'] = match is not None
        if match:
            ensure_rolle(beitrag, match, engine)
        sl.upsert(engine, table, beitrag, unique=KEYS)

