import logging
from collections import defaultdict
from datetime import datetime

import sqlaload as sl

from offenesparlament.core import db
from offenesparlament.data.persons.load import lazyload_person
from offenesparlament.model.util import to_date
from offenesparlament.model import Person, Sitzung, Debatte, Zitat, Rede

log = logging.getLogger(__name__)


def load_sitzung(engine, indexer, wp, session):
    table = sl.get_table(engine, 'webtv_speech')
    data = sl.find_one(engine, table, wp=wp, session=session)
    log.info("Loading Sitzung: %s/%s...", wp, session)
    sitzung = Sitzung.query.filter_by(wahlperiode=wp, nummer=session).first()
    if sitzung is None:
        sitzung = Sitzung()
        sitzung.wahlperiode = wp
        sitzung.nummer = session
    sitzung.titel = data.get('session_name')
    sitzung.date = to_date(data.get('session_date'))
    sitzung.source_url = data.get('session_url')

    db.session.add(sitzung)
    db.session.flush()
    indexer.add(sitzung)

    load_debatten(engine, indexer, sitzung)
    db.session.commit()
    return sitzung


def load_debatten(engine, indexer, sitzung):
    WebTV_Speech = sl.get_table(engine, 'webtv_speech')
    zitate = list(sl.find(engine, WebTV_Speech, wp=str(sitzung.wahlperiode),
        session=str(sitzung.nummer)))
    debatten = dict([(z['item_id'], z) for z in zitate])
    speeches = list(sl.find(engine, sl.get_table(engine, 'speech'),
        wahlperiode=int(sitzung.wahlperiode), sitzung=int(sitzung.nummer)))
    for i, data in debatten.items():
        log.info("Loading  -> Debatte: %s..." % data.get('item_label'))
        debatte = Debatte.query.filter_by(
                sitzung=sitzung,
                nummer=data.get('item_id')
                ).first()
        if debatte is None:
            debatte = Debatte()
        debatte.sitzung = sitzung
        debatte.nummer = data.get('item_id')
        debatte.tops = data.get('item_key')
        debatte.titel = data.get('item_label')
        debatte.text = data.get('item_description')

        db.session.add(debatte)
        db.session.flush()
        indexer.add(debatte)
        
        dzitate = filter(lambda z: z['item_id'] == data['item_id'], zitate)
        reden = load_reden(engine, indexer, debatte, dzitate)
        load_zitate(engine, indexer, debatte, dzitate, speeches, reden)
        db.session.commit()
        indexer.add_many(reden.values())

def load_reden(engine, indexer, debatte, zitate):
    reden = {}
    for zitat in zitate:
        if zitat['speech_id'] in reden:
            continue
        rede = Rede.query.filter_by(webtv_id=zitat['speech_id']).first()
        if rede is None:
            rede = Rede()
            rede.webtv_id = zitat['speech_id']
        rede.redner = lazyload_person(engine, indexer,
                                zitat['fingerprint'])
        rede.debatte = debatte
        rede.sitzung = debatte.sitzung
        db.session.add(rede)
        db.session.flush()
        reden[zitat['speech_id']] = rede
    return reden

def load_zitate(engine, indexer, debatte, zitate, speeches, reden):
    for data in zitate:
        f = lambda s: int(s['wahlperiode']) == int(data['wp']) and \
                      int(s['sitzung']) == int(data['session']) and \
                      int(s['sequence']) == int(data['sequence'])
        speech = filter(f, speeches).pop()
        zitat = Zitat.query.filter_by(
                debatte=debatte,
                sequenz=speech['sequence']).first()
        if zitat is None:
            zitat = Zitat()
        zitat.sitzung = debatte.sitzung
        zitat.debatte = debatte
        zitat.sequenz = speech['sequence']
        zitat.rede = reden[data['speech_id']]
        zitat.text = speech['text']
        zitat.typ = speech['type']
        zitat.sprecher = speech['speaker']
        zitat.source_url = speech['source_url']
        zitat.person = lazyload_person(engine, indexer,
                speech['fingerprint'])

        db.session.add(zitat)
        db.session.flush()

