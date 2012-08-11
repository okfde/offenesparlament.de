import sys
import logging
from collections import defaultdict
from datetime import datetime

import sqlaload as sl

from offenesparlament.core import etl_engine

from offenesparlament.core import db
from offenesparlament.model import Gremium, NewsItem, Person, Rolle, \
        Wahlkreis, obleute, mitglieder, stellvertreter, Ablauf, \
        Position, Beschluss, Beitrag, Zuweisung, Referenz, Dokument, \
        Schlagwort, Sitzung, Debatte, Zitat, Stimme, Abstimmung

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.NOTSET)


def date(text):
    try:
        return datetime.strptime(text, "%Y-%m-%dT%H:%M:%S")
    except:
        pass


def load_gremien(engine):
    log.info("Loading gremien into production DB...")
    _GremiumSource = sl.get_table(engine, 'gremium')
    for data in sl.all(engine, _GremiumSource):
        gremium = Gremium.query.filter_by(key=data.get('key')).first()
        if gremium is None:
            gremium = Gremium()
        gremium.key = data.get('key')
        gremium.source_url = data.get('source_url')
        gremium.name = data.get('name')
        gremium.typ = data.get('type')
        gremium.url = data.get('url')
        gremium.aufgabe = data.get('aufgabe')
        gremium.rss_url = data.get('rss_url')
        gremium.image_url = data.get('image_url')
        gremium.image_copyright = data.get('image_copyright')
        db.session.add(gremium)
    db.session.commit()


def load_news(engine):
    log.info("Loading news into production DB...")
    _NewsSource = sl.get_table(engine, 'news')
    for data in sl.all(engine, _NewsSource):
        news = NewsItem.query.filter_by(
                source_url=data.get('source_url')).first()
        if news is None:
            news = NewsItem()
        news.key = data.get('key')
        news.source_url = data.get('source_url')
        news.title = data.get('title')
        news.text = data.get('text')
        news.date = date(data.get('date'))
        news.image_url = data.get('image_url')
        news.image_copyright = data.get('image_copyright')
        news.image_changed_at = date(data.get('image_changed_at'))

        if data.get('gremium'):
            gremium = Gremium.query.filter_by(
                    key=data.get('gremium')).first()
            if gremium is None:
                log.error("Gremium %s not found!" % data.get('gremium'))
            else:
                news.gremium = gremium
        db.session.add(news)
    db.session.commit()


def load_persons(engine):
    log.info("Loading persons into production DB...")
    db.session.commit()
    db.session.execute(obleute.delete())
    db.session.execute(mitglieder.delete())
    db.session.execute(stellvertreter.delete())

    _PersonSource = sl.get_table(engine, 'person')
    for data in sl.all(engine, _PersonSource):
        person = Person.query.filter_by(
                fingerprint=data.get('fingerprint')).first()
        if person is None:
            person = Person()

        person.slug = data.get('slug')
        person.fingerprint = data.get('fingerprint')
        log.info("      -> %s" % person.fingerprint)
        person.source_url = data.get('source_url')
        person.mdb_id = data.get('mdb_id')
        person.vorname = data.get('vorname')
        person.nachname = data.get('nachname')
        person.adelstitel = data.get('adelstitel')
        person.titel = data.get('titel')
        person.ort = data.get('ort')
        person.geburtsdatum = data.get('geburtsdatum')
        person.religion = data.get('religion')
        person.hochschule = data.get('hochschule')
        person.beruf = data.get('beruf')
        person.berufsfeld = data.get('berufsfeld')
        person.geschlecht = data.get('geschlecht')
        person.familienstand = data.get('familienstand')
        person.kinder = data.get('kinder')
        person.partei = data.get('partei')
        person.land = data.get('land')
        person.bio_url = data.get('bio_url')
        person.bio = data.get('bio')
        person.wissenswertes = data.get('wissenswertes')
        person.homepage_url = data.get('homepage_url')
        person.telefon = data.get('telefon')
        person.homepage_url = data.get('homepage_url')
        person.angaben = data.get('angaben')
        person.foto_url = data.get('foto_url')
        person.foto_copyright = data.get('foto_copyright')
        person.reden_plenum_url = data.get('reden_plenum_url')
        person.reden_plenum_rss_url = data.get('reden_plenum_rss_url')
        person.twitter_url = data.get('twitter_url')
        person.facebook_url = data.get('facebook_url')
        person.awatch_url = data.get('awatch_url')
        db.session.add(person)
        db.session.flush()
        mdb_rolle = load_rollen(engine, person, data)
        load_gremium_mitglieder(engine, person, mdb_rolle)

        db.session.commit()


def load_wahlkreis(engine, rolle, data):
    if data.get('wk_nummer'):
        wk = Wahlkreis.query.filter_by(
            nummer=data.get('wk_nummer')).first()
        if wk is None:
            wk = Wahlkreis()
        wk.nummer = data.get('wk_nummer')
        wk.name = data.get('wk_name')
        wk.url = data.get('wk_url')
        db.session.add(wk)
        return wk


def load_rollen(engine, person, data):
    _RolleSource = sl.get_table(engine, 'rolle')
    mdb_rolle = None
    for rdata in sl.find(engine, _RolleSource, fingerprint=data['fingerprint']):
        rolle = Rolle.query.filter_by(
                person=person,
                funktion=rdata.get('funktion'),
                ressort=rdata.get('ressort'),
                fraktion=rdata.get('fraktion'),
                land=rdata.get('land')).first()
        if rolle is None:
            rolle = Rolle()

        rolle.person = person
        rolle.mdb_id = rdata.get('mdb_id')
        rolle.status = rdata.get('status')
        rolle.funktion = rdata.get('funktion')
        rolle.fraktion = rdata.get('fraktion')
        rolle.gewaehlt = rdata.get('gewaehlt')
        rolle.ressort = rdata.get('ressort')
        rolle.land = rdata.get('land')
        rolle.austritt = date(rdata.get('austritt'))

        if rdata.get('mdb_id'):
            rolle.wahlkreis = load_wahlkreis(engine, rolle, data)
            mdb_rolle = rolle
        db.session.add(rolle)
    return mdb_rolle


def load_gremium_mitglieder(engine, person, rolle):
    _GremiumMitglieder = sl.get_table(engine, 'gremium_mitglieder')
    for gmdata in sl.find(engine, _GremiumMitglieder,
                          person_source_url=person.source_url):
        gremium = Gremium.query.filter_by(key=gmdata['gremium_key']).first()
        if gremium is None:
            log.error("Gremium not found: %s" % gmdata['gremium_key'])
        role = gmdata['role']
        if role == 'obleute':
            gremium.obleute.append(person)
        elif role == 'vorsitz':
            gremium.vorsitz = person
        elif role == 'stellv_vorsitz':
            gremium.stellv_vorsitz = person
        elif role == 'mitglied':
            gremium.mitglieder.append(person)
        elif role == 'stellv_mitglied':
            gremium.stellvertreter.append(person)
        else:
            raise TypeError("Invalid ms type: %s" % role)


def load_ablaeufe(engine):
    _Ablauf = sl.get_table(engine, 'ablauf')

    for i, data in enumerate(sl.find(engine, _Ablauf, wahlperiode=str(17))):
        log.info("Loading Ablauf: %s..." % data['titel'])
        load_ablauf(engine, data)
        if i % 500 == 0:
            db.session.commit()
    db.session.commit()


def load_ablauf(engine, data):
    ablauf = Ablauf.query.filter_by(
            wahlperiode=data.get('wahlperiode'),
            key=data.get('key')).first()
    if ablauf is None:
        ablauf = Ablauf()

    ablauf_id = data.get('ablauf_id')
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
    for sw in sl.find(engine, _Schlagwort, wahlperiode=ablauf.wahlperiode,
            key=ablauf.key):
        wort = Schlagwort()
        wort.name = sw['wort']
        db.session.add(wort)
        worte.append(wort)
    ablauf.schlagworte = worte

    _Referenz = sl.get_table(engine, 'referenz')
    for ddata in sl.find(engine, _Referenz, wahlperiode=ablauf.wahlperiode,
            ablauf_key=ablauf.key):
        dokument = load_dokument(ddata, engine)
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
    for position in sl.find(engine, _Position, ablauf_id=ablauf_id):
        load_position(position, ablauf_id, ablauf, engine)


def load_position(data, ablauf_id, ablauf, engine):
    position = Position.query.filter_by(
            ablauf=ablauf,
            urheber=data.get('urheber'),
            fundstelle=data.get('fundstelle')).first()
    if position is not None:
        return
    position = Position()
    position.key = data.get('hash')
    position.zuordnung = data.get('zuordnung')
    position.urheber = data.get('urheber')
    position.fundstelle = data.get('fundstelle')
    position.fundstelle_url = data.get('fundstelle_url')
    position.date = date(data.get('date'))
    position.quelle = data.get('quelle')
    position.typ = data.get('typ')
    position.ablauf = ablauf

    if data.get('debatte_item_id'):
        dq = Debatte.query.filter(Debatte.nummer==data.get('debatte_item_id'))
        dq = dq.filter(Debatte.sitzung.wahlperiode==data.get('debatte_wp'))
        dq = dq.filter(Debatte.sitzung.nummer==data.get('debatte_session'))
        position.debatte = dq.first()

    _Referenz = sl.get_table(engine, 'referenz')
    for ddata in sl.find(engine, _Referenz, fundstelle=position.fundstelle,
            urheber=position.urheber, ablauf_id=ablauf_id):
        position.dokument = load_dokument(ddata, engine)

    db.session.add(position)

    _Zuweisung = sl.get_table(engine, 'zuweisung')
    for zdata in sl.find(engine, _Zuweisung, fundstelle=position.fundstelle,
            urheber=position.urheber, ablauf_id=ablauf_id):
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
            urheber=position.urheber, ablauf_id=ablauf_id):
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
            urheber=position.urheber, ablauf_id=ablauf_id, matched=True):
        load_beitrag(bdata, position, engine)


def load_beitrag(data, position, engine):
    beitrag = Beitrag()
    beitrag.seite = data.get('seite')
    beitrag.art = data.get('art')
    beitrag.position = position

    beitrag.person = Person.query.filter_by(
            fingerprint=data.get('fingerprint')
            ).first()
    beitrag.rolle = Rolle.query.filter_by(
            person=beitrag.person,
            funktion=data.get('funktion'),
            ressort=data.get('ressort'),
            land=data.get('land')).first()
    db.session.add(beitrag)


def load_dokument(data, engine):
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
    return dokument


def load_sitzungen(engine):
    WebTV = sl.get_table(engine, 'webtv_speech')
    for session in sl.distinct(engine, WebTV,
        'wp', 'session', 'session_name', 'session_date'):
        load_sitzung(engine, session)


def load_sitzung(engine, session):
    log.info("Loading Sitzung: %s/%s..." % (session.get('wp'), session.get('session')))
    sitzung = Sitzung.query.filter_by(
            wahlperiode=session.get('wp'),
            nummer=session.get('session')
            ).first()
    if sitzung is None:
        sitzung = Sitzung()
        sitzung.wahlperiode = session.get('wp')
        sitzung.nummer = session.get('session')
    else:
        return
    sitzung.titel = session.get('session_name')
    sitzung.date = date(session.get('session_date'))
    sitzung.source_url = session.get('session_url')

    db.session.add(sitzung)
    db.session.flush()

    load_debatten(engine, sitzung)
    db.session.commit()
    return sitzung


def load_debatten(engine, sitzung):
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

        dzitate = filter(lambda z: z['item_id'] == data['item_id'], zitate)
        load_zitate(engine, debatte, dzitate, speeches)
        db.session.commit()


SPEAKERS = {}
def load_zitate(engine, debatte, zitate, speeches):
    for data in zitate:
        f = lambda s: int(s['wahlperiode']) == int(data['wp']) and \
                      int(s['sitzung']) == int(data['session']) and \
                      int(s['sequence']) == int(data['sequence'])
        speech = filter(f, speeches).pop()
        #print speech

        zitat = Zitat.query.filter_by(
                debatte=debatte,
                sequenz=speech['sequence']).first()
        if zitat is None:
            zitat = Zitat()
        zitat.sitzung = debatte.sitzung
        zitat.debatte = debatte
        zitat.sequenz = speech['sequence']
        zitat.text = speech['text']
        zitat.typ = speech['type']
        zitat.speech_id = data['speech_id']
        zitat.sprecher = speech['speaker']
        zitat.redner = data['speaker']
        zitat.source_url = speech['source_url']

        if speech['fingerprint']:
            if speech['fingerprint'] in SPEAKERS:
                zitat.person = SPEAKERS[speech['fingerprint']]
            else:
                zitat.person = Person.query.filter_by(
                    fingerprint=speech['fingerprint']
                    ).first()
                SPEAKERS[speech['fingerprint']] = zitat.person

        db.session.add(zitat)
        #db.session.flush()


def load_abstimmungen(engine):
    _Abstimmung = sl.get_table(engine, 'abstimmung')
    i = 0
    for row in sl.distinct(engine, _Abstimmung, 'subject', 'date'):
        thema = row.get('subject')
        abst = Abstimmung.query.filter_by(thema=thema).first()
        if abst is None:
            abst = Abstimmung()
            abst.thema = thema
            abst.datum = date(row.get('date'))
        db.session.add(abst)
        for stimme_ in sl.find(engine, _Abstimmung, subject=thema,
            matched=True):
            if i % 1000 == 0:
                sys.stdout.write(".")
                sys.stdout.flush()
            i += 1
            person = Person.query.filter_by(
                fingerprint=stimme_.get('fingerprint')).first()
            if person is None:
                continue
            stimme = Stimme.query.filter_by(
                abstimmung=abst).filter_by(
                person=person).first()
            if stimme is not None:
                continue
            stimme = Stimme()
            stimme.entscheidung = stimme_['vote']
            stimme.person = person
            stimme.abstimmung = abst
            db.session.add(stimme)
        db.session.commit()


def load(engine):
    load_gremien(engine)
    #load_news(engine)
    load_persons(engine)
    load_sitzungen(engine)
    load_ablaeufe(engine)
    load_abstimmungen(engine)


def aggregate():
    from offenesparlament.aggregates import make_current_schlagwort, \
        make_period_sachgebiete, make_person_schlagworte
    make_current_schlagwort()
    make_period_sachgebiete()
    make_person_schlagworte()
