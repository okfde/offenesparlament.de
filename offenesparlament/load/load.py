import sys
import logging
from datetime import datetime

from webstore.client import WebstoreClientException, URL as WebStore

from offenesparlament.core import db
from offenesparlament.model import Gremium, NewsItem, Person, Rolle, \
        Wahlkreis, obleute, mitglieder, stellvertreter, Ablauf, \
        Position, Beschluss, Beitrag, Zuweisung, Referenz, Dokument, \
        Schlagwort, Sitzung, Debatte, Zitat, DebatteZitat

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.NOTSET)

def date(text):
    try:
        return datetime.strptime(text, "%Y-%m-%dT%H:%M:%S")
    except:
        pass

def load_gremien(ws):
    log.info("Loading gremien into production DB...")
    GremiumSource = ws['gremium']
    for data in GremiumSource:
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

def load_news(ws):
    log.info("Loading news into production DB...")
    NewsSource = ws['news']
    for data in NewsSource:
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

def load_persons(ws):
    log.info("Loading persons into production DB...")
    db.session.commit()
    db.session.execute(obleute.delete())
    db.session.execute(mitglieder.delete())
    db.session.execute(stellvertreter.delete())

    PersonSource = ws['person']
    for data in PersonSource:
        person = Person.query.filter_by(
                source_url=data.get('source_url')).first()
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
        db.session.add(person)
        db.session.flush()
        mdb_rolle = load_rollen(ws, person, data)
        load_gremium_mitglieder(ws, person, mdb_rolle)
        
        db.session.commit()

def load_wahlkreis(ws, rolle, data):
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

def load_rollen(ws, person, data):
    RolleSource = ws['rolle']
    mdb_rolle = None
    for rdata in RolleSource.traverse(fingerprint=data['fingerprint']):
        rolle = Rolle.query.filter_by(
                person=person, funktion=rdata.get('funktion')).first()
        if rolle is None:
            rolle = Rolle()

        rolle.person = person
        rolle.mdb_id = rdata.get('mdb_id')
        rolle.status = rdata.get('status')
        rolle.funktion = rdata.get('funktion')
        rolle.fraktion = rdata.get('fraktion')
        rolle.gewaehlt = rdata.get('gewaehlt')
        rolle.rolle = rdata.get('rolle')
        rolle.ressort = rdata.get('ressort')
        rolle.land = rdata.get('land')
        rolle.austritt = date(rdata.get('austritt'))

        if rdata.get('mdb_id'):
            rolle.wahlkreis = load_wahlkreis(ws, rolle, data)
            mdb_rolle = rolle
        db.session.add(rolle)
    return mdb_rolle

def load_gremium_mitglieder(ws, person, rolle):
    for gmdata in ws['gremium_mitglieder']\
            .traverse(person_source_url=person.source_url):
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

def load_ablaeufe(ws):
    for data in ws['ablauf']:
        log.info("Loading Ablauf: %s..." % data['titel'])
        load_ablauf(ws, data)

def load_ablauf(ws, data):
    ablauf = Ablauf.query.filter_by(
            wahlperiode=data.get('wahlperiode'), 
            key=data.get('key')).first()
    if ablauf is None:
        ablauf = Ablauf()

    ablauf.key = data.get('key')
    ablauf.source_url = data.get('source_url')
    ablauf.wahlperiode = data.get('wahlperiode')
    ablauf.typ = data.get('typ')
    ablauf.klasse = data.get('class')
    ablauf.titel = data.get('titel')
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
    for sw in ws['schlagwort'].traverse(wahlperiode=ablauf.wahlperiode,
            key=ablauf.key):
        wort = Schlagwort()
        wort.name = sw['wort']
        db.session.add(wort)
        worte.append(wort)
    ablauf.schlagworte = worte

    for ddata in ws['referenz'].traverse(wahlperiode=ablauf.wahlperiode,
            ablauf_key=ablauf.key):
        dokument = load_dokument(ddata, ws)
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

    for position in ws['position'].traverse(
            ablauf_source_url=ablauf.source_url):
        load_position(position, ablauf, ws)

    db.session.commit()

def load_position(data, ablauf, ws):
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

    for ddata in ws['referenz'].traverse(fundstelle=position.fundstelle,
            urheber=position.urheber, ablauf_source_url=ablauf.source_url):
        position.dokument = load_dokument(ddata, ws)

    db.session.add(position)

    for zdata in ws['zuweisung'].traverse(fundstelle=position.fundstelle,
            urheber=position.urheber, ablauf_source_url=ablauf.source_url):
        zuweisung = Zuweisung()
        zuweisung.text = zdata['text']
        zuweisung.federfuehrung = True if \
                str(zdata['federfuehrung'])=='True' else False
        zuweisung.gremium = Gremium.query.filter_by(
                key=zdata.get('gremium_key')).first()
        zuweisung.position = position
        db.session.add(zuweisung)
    
    try:
        for bdata in ws['beschluss'].traverse(fundstelle=position.fundstelle,
                urheber=position.urheber, ablauf_source_url=ablauf.source_url):
            beschluss = Beschluss()
            beschluss.seite = bdata['seite']
            beschluss.tenor = bdata['tenor']
            beschluss.dokument_text = bdata['dokument_text']
            db.session.add(beschluss)
    except WebstoreClientException:
        pass


    for bdata in ws['beitrag'].traverse(fundstelle=position.fundstelle,
            urheber=position.urheber, ablauf_source_url=ablauf.source_url):
        load_beitrag(bdata, position, ws)

def load_beitrag(data, position, ws):
    beitrag = Beitrag()
    beitrag.seite = data.get('seite')
    beitrag.art = data.get('art')
    beitrag.position = position

    beitrag.person = Person.query.filter_by(
            fingerprint=data.get('fingerprint')
            ).first()
    beitrag.rolle = Rolle.query.filter_by(
            person=beitrag.person,
            funktion=data.get('funktion')).first()
    db.session.add(beitrag)

def load_dokument(data, ws):
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

def load_debatten(ws):
    sitzungen = {}
    for speech in ws['mediathek']:
        sitz = (speech['wahlperiode'], speech['meeting_nr'])
        if not sitz in sitzungen:
            sitzungen[sitz] = load_sitzung(ws, speech)
        sitzung = sitzungen[sitz]
        log.info("Loading Debatte: %s/%s - %s..." % (
            speech.get('wahlperiode'),
            speech.get('meeting_nr'), 
            speech.get('top_title')))
        debatte = Debatte.query.filter_by(
                sitzung=sitzung,
                source_url=speech.get('top_source_url')
                ).first()
        if debatte is None:
            debatte = Debatte()
            debatte.sitzung = sitzung
            debatte.source_url = speech.get('top_source_url')
        debatte.nummer = speech.get('top_nr')
        debatte.titel = speech.get('top_title')
        debatte.text = speech.get('top_text')
        debatte.pdf_url = speech.get('top_pdf_url_plain')
        debatte.pdf_page = speech.get('top_pdf_url_pages')
        debatte.video_url = speech.get('top_mp4_url')

        db.session.add(debatte)
        db.session.commit()

def load_sitzung(ws, speech):
    log.info("Loading Sitzung: %s/%s..." % (speech.get('wahlperiode'),
        speech.get('meeting_nr')))
    sitzung = Sitzung.query.filter_by(
            wahlperiode=speech.get('wahlperiode'),
            nummer=speech.get('meeting_nr')
            ).first()
    if sitzung is None:
        sitzung = Sitzung()
        sitzung.wahlperiode = speech.get('wahlperiode')
        sitzung.nummer = speech.get('meeting_nr')
    
    sitzung.titel = speech.get('meeting_title')
    sitzung.text = speech.get('meeting_text')
    sitzung.date = date(speech.get('meeting_date'))
    sitzung.pdf_url = speech.get('meeting_pdf_url_plain')
    sitzung.pdf_page = speech.get('meeting_pdf_url_pages')
    sitzung.video_url = speech.get('meeting_mp4_url')
    sitzung.source_url = speech.get('meeting_source_url')

    db.session.add(sitzung)
    db.session.flush()
    return sitzung

def load_zitate(ws):
    sitzungen = {}
    mediathek = dict([(m['speech_source_url'], m) for m in ws['mediathek']])
    sys.stdout.write("Loading transcripts")
    sys.stdout.flush()
    for speech in ws['speech']:
        sys.stdout.write(".")
        sys.stdout.flush()
        s = (speech['wahlperiode'], speech['sitzung'])
        if s not in sitzungen:
            sitzungen[s] = Sitzung.query.filter_by(
                wahlperiode=speech.get('wahlperiode'),
                nummer=speech.get('sitzung')
                ).first()
        sitzung = sitzungen[s]

        zitat = Zitat.query.filter_by(
                sitzung=sitzung,
                sequenz=speech['sequence']).first()
        if zitat is None:
            zitat = Zitat()
        zitat.sitzung = sitzung
        zitat.sequenz = speech['sequence']
        zitat.text = speech['text']
        zitat.typ = speech['type']
        zitat.sprecher = speech['speaker']
        zitat.source_url = speech['source_url']

        if speech['fingerprint']:
            zitat.person = Person.query.filter_by(
                fingerprint=speech['fingerprint']
                ).first()

        db.session.add(zitat)
        db.session.flush()
        load_debatte_zitate(ws, zitat, mediathek)

        db.session.commit()

def load_debatte_zitate(ws, zitat, mediathek):
    if zitat.sitzung is None:
        return
    spme = ws['speech_mediathek']
    for item in spme.traverse(wahlperiode=zitat.sitzung.wahlperiode,
            sitzung=zitat.sitzung.nummer, sequence=zitat.sequenz):
        sp = mediathek[item['mediathek_url']]
        debatte = Debatte.query.filter_by(
                source_url=sp['top_source_url']).first()
        dz = DebatteZitat.query.filter_by(zitat=zitat,
                debatte=debatte).first()
        if dz is None:
            dz = DebatteZitat()
            dz.debatte = debatte
            dz.zitat = zitat
        dz.nummer = sp['speech_nr']
        dz.pdf_url = sp['speech_pdf_url_plain']
        dz.pdf_page = sp['speech_pdf_url_pages']
        dz.video_url = sp['speech_mp4_url']
        db.session.add(dz)


def load(ws):
    load_gremien(ws)
    #load_news(ws)
    load_persons(ws)
    load_ablaeufe(ws)
    load_debatten(ws)
    load_zitate(ws)

if __name__ == '__main__':
    assert len(sys.argv)==2, "Need argument: webstore-url!"
    ws, _ = WebStore(sys.argv[1])
    print "SOURCE", ws
    load(ws)


