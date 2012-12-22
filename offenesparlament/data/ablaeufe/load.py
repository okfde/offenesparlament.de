import logging

import sqlaload as sl

from offenesparlament.core import db
from offenesparlament.model.util import to_date
from offenesparlament.model import Gremium, Person, Rolle, Ablauf, \
        Position, Beschluss, Beitrag, Zuweisung, Referenz, Dokument, \
        Schlagwort, Sitzung, Debatte
from offenesparlament.data.persons.load import lazyload_person

log = logging.getLogger(__name__)


def load_ablauf(engine, indexer, data):
    ablauf = Ablauf.query.filter_by(source_url=data.get('source_url')).first()
    if ablauf is None:
        ablauf = Ablauf()

    ablauf.key = data.get('key')
    ablauf.source_url = data.get('source_url')
    ablauf.wahlperiode = data.get('wahlperiode')
    ablauf.typ = data.get('typ')
    ablauf.klasse = data.get('class')
    ablauf.titel = data.get('titel')
    if not len(ablauf.titel):
        log.error("No titel!")
        return

    ablauf.initiative = data.get('initiative')
    ablauf.stand = data.get('stand')
    ablauf.signatur = data.get('signatur')
    ablauf.gesta_id = data.get('gesta_id')
    ablauf.eu_dok_nr = data.get('eu_dok_nr')
    ablauf.eur_lex_url = data.get('eur_lex_url')
    ablauf.eur_lex_pdf = data.get('eur_lex_pdf')
    ablauf.consilium_url = data.get('consilium_url')
    ablauf.abstrakt = data.get('abstrakt')
    ablauf.zustimmungsbeduerftig = data.get('zustimmungsbeduerftig')
    ablauf.sachgebiet = data.get('sachgebiet')
    ablauf.abgeschlossen = True if str(data.get('abgeschlossen')) \
            == 'True' else False
    db.session.add(ablauf)
    db.session.flush()

    worte = []
    _Schlagwort = sl.get_table(engine, 'schlagwort')
    for sw in sl.find(engine, _Schlagwort, source_url=ablauf.source_url):
        wort = Schlagwort()
        wort.name = sw['wort']
        db.session.add(wort)
        worte.append(wort)
    ablauf.schlagworte = worte

    _Referenz = sl.get_table(engine, 'referenz')
    for ddata in sl.find(engine, _Referenz, source_url=ablauf.source_url):
        dokument = load_dokument(engine, indexer, ddata)
        referenz = Referenz.query.filter_by(
                dokument=dokument,
                seiten=ddata.get('seiten'),
                ).filter(Referenz.ablaeufe.any(id=ablauf.id)).first()
        if referenz is None:
            referenz = Referenz()
            referenz.ablaeufe.append(ablauf)
            referenz.dokument = dokument
        referenz.seiten = ddata.get('seiten')
        referenz.text = ddata.get('text')

    _Position = sl.get_table(engine, 'position')
    for position in sl.find(engine, _Position, source_url=ablauf.source_url):
        load_position(engine, indexer, ablauf, position)

    db.session.commit()
    indexer.add(ablauf)


def load_position(engine, indexer, ablauf, data):
    position = Position.query.filter_by(
            ablauf=ablauf,
            urheber=data.get('urheber'),
            fundstelle=data.get('fundstelle')).first()
    if position is not None:
        indexer.add(position)
        return
    position = Position()
    position.key = data.get('hash')
    position.zuordnung = data.get('zuordnung')
    position.urheber = data.get('urheber')
    position.fundstelle = data.get('fundstelle')
    position.fundstelle_url = data.get('fundstelle_url')
    position.date = to_date(data.get('date'))
    position.quelle = data.get('quelle')
    position.typ = data.get('typ')
    position.ablauf = ablauf

    if data.get('debatte_item_id'):
        dq = Debatte.query.filter(Debatte.nummer==data.get('debatte_item_id'))
        dq = dq.join(Sitzung)
        dq = dq.filter(Sitzung.wahlperiode==data.get('debatte_wp'))
        dq = dq.filter(Sitzung.nummer==data.get('debatte_session'))
        position.debatte = dq.first()

    _Referenz = sl.get_table(engine, 'referenz')
    for ddata in sl.find(engine, _Referenz, fundstelle=position.fundstelle,
            urheber=position.urheber, source_url=ablauf.source_url):
        position.dokument = load_dokument(engine, indexer, ddata)

    db.session.add(position)
    db.session.flush()

    _Zuweisung = sl.get_table(engine, 'zuweisung')
    for zdata in sl.find(engine, _Zuweisung, fundstelle=position.fundstelle,
            urheber=position.urheber, source_url=ablauf.source_url):
        zuweisung = Zuweisung()
        zuweisung.text = zdata['text']
        zuweisung.federfuehrung = True if \
                str(zdata['federfuehrung']) == 'True' else False
        zuweisung.gremium = Gremium.query.filter_by(
                key=zdata.get('gremium_key')).first()
        zuweisung.position = position
        db.session.add(zuweisung)

    _Beschluss = sl.get_table(engine, 'beschluss')
    for bdata in sl.find(engine, _Beschluss, fundstelle=position.fundstelle,
            urheber=position.urheber, source_url=ablauf.source_url):
        beschluss = Beschluss()
        beschluss.position = position
        beschluss.seite = bdata['seite']
        beschluss.tenor = bdata['tenor']
        beschluss.dokument_text = bdata['dokument_text'] or ''
        for dokument_name in beschluss.dokument_text.split(','):
            dokument_name = dokument_name.strip()
            dok = Dokument.query.filter_by(nummer=dokument_name).first()
            if dok is not None:
                beschluss.dokumente.append(dok)
        db.session.add(beschluss)

    _Beitrag = sl.get_table(engine, 'beitrag')
    for bdata in sl.find(engine, _Beitrag, fundstelle=position.fundstelle,
            urheber=position.urheber, source_url=ablauf.source_url, matched=True):
        load_beitrag(engine, indexer, position, bdata)

    db.session.refresh(position)
    indexer.add(position)


def load_beitrag(engine, indexer, position, data):
    beitrag = Beitrag()
    beitrag.seite = data.get('seite')
    beitrag.art = data.get('art')
    beitrag.position = position

    beitrag.person = lazyload_person(engine, indexer,
            data.get('fingerprint'))
    beitrag.rolle = Rolle.query.filter_by(
            person=beitrag.person,
            funktion=data.get('funktion'),
            ressort=data.get('ressort'),
            land=data.get('land')).first()
    if beitrag.person is not None and beitrag.rolle is None:
        beitrag.rolle = Rolle()
        beitrag.rolle.person = beitrag.person
        beitrag.rolle.funktion = data.get('funktion')
        beitrag.rolle.ressort = data.get('ressort')
        beitrag.rolle.land = data.get('land')
        db.session.add(beitrag.rolle)
    db.session.add(beitrag)


def load_dokument(engine, indexer, data):
    dokument = Dokument.query.filter_by(
            hrsg=data.get('hrsg'),
            typ=data.get('typ'),
            nummer=data.get('nummer')).first()
    if dokument is None:
        dokument = Dokument()
        dokument.hrsg = data.get('hrsg')
        dokument.typ = data.get('typ')
        dokument.nummer = data.get('nummer')
    if data.get('link'):
        dokument.link = data.get('link')
    db.session.add(dokument)
    db.session.flush()
    indexer.add(dokument)
    return dokument

