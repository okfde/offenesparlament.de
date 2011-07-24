#coding: utf-8
import logging
from lxml import etree
from datetime import datetime

from offenesparlament.core import db
from offenesparlament.model import Person, Rolle, Wahlkreis, Gremium

MDB_INDEX_URL = "http://www.bundestag.de/xml/mdb/index.xml"

log = logging.getLogger(__name__)

def get_node_gremium(node):
    key = node.get('id')
    g = Gremium.query.filter_by(key=key).first()
    if g is None:
        g = Gremium()
        g.key = key
        g.type = 'sonstiges'
        g.name = node.findtext('gremiumName')
        g.url = node.findtext('gremiumURL')
        db.session.add(g)
    return g

def load_index(): 
    doc = etree.parse(MDB_INDEX_URL)
    for info_url in doc.findall("//mdbInfoXMLURL"):
        load_mdb(info_url.text)

def load_mdb(url):
    doc = etree.parse(url)
    p = Person.query.filter_by(source_url=url).first()
    if p is None:
        p = Person()
        r = Rolle()
    else:
        r = Rolle()
        for rc in p.rollen:
            if rc.funktion == 'MdB':
                r = rc

    p.source_url = url
    r.funktion = 'MdB'
    r.person = p
    r.mdb_id = int(doc.findtext('//mdbID'))
    r.status = doc.find('//mdbID').get('status')
    if doc.findtext('//mdbAustrittsdatum'):
        r.austritt = datetime.strptime(doc.findtext('//mdbAustrittsdatum'),
                                       '%d.%m.%Y')
    p.vorname = doc.findtext('//mdbVorname')
    p.nachname = doc.findtext('//mdbZuname')
    p.adelstitel = doc.findtext('//mdbAdelstitel')
    p.titel = doc.findtext('//mdbAkademischerTitel')
    p.ort = doc.findtext('//mdbOrtszusatz')
    log.info('MdB: %s %s (%s)' % (p.vorname, p.nachname, p.ort))
    p.geburtsdatum = doc.findtext('//mdbGeburtsdatum')
    p.religion = doc.findtext('//mdbReligionKonfession')
    p.hochschule = doc.findtext('//mdbHochschulbildung')
    p.beruf = doc.findtext('//mdbBeruf')
    p.berufsfeld = doc.find('//mdbBeruf').get('berufsfeld')
    p.geschlecht = doc.findtext('//mdbGeschlecht')
    p.familienstand = doc.findtext('//mdbFamilienstand')
    p.kinder = doc.findtext('//mdbAnzahlKinder')
    r.fraktion = doc.findtext('//mdbFraktion')
    p.partei = doc.findtext('//mdbPartei')
    p.land = doc.findtext('//mdbLand')
    r.gewaehlt = doc.findtext('//mdbGewaehlt')
    p.bio_url = doc.findtext('//mdbBioURL')
    p.bio = doc.findtext('//mdbBiografischeInformationen')
    p.wissenswertes = doc.findtext('//mdbWissenswertes')
    p.homepage_url = doc.findtext('//mdbHomepageURL')
    p.telefon = doc.findtext('//mdbTelefon')
    p.angaben = doc.findtext('//mdbVeroeffentlichungspflichtigeAngaben')
    p.foto_url = doc.findtext('//mdbFotoURL')
    p.foto_copyright = doc.findtext('//mdbFotoCopyright')
    p.reden_plenum_url = doc.findtext('//mdbRedenVorPlenumURL')
    p.reden_plenum_rss_url = doc.findtext('//mdbRedenVorPlenumRSS')
    
    wk_nummer = doc.findtext('//mdbWahlkreisNummer')
    if wk_nummer:
        wk = Wahlkreis.query.filter_by(nummer=wk_nummer).first()
        if wk is None:
            wk = Wahlkreis()
        wk.nummer = wk_nummer
        wk.name = doc.findtext('//mdbWahlkreisName') 
        wk.url = doc.findtext('//mdbWahlkreisURL')
        r.wahlkreis = wk
        db.session.add(wk)

    for website in doc.findall('//mdbSonstigeWebsite'):
        type_ = website.findtext('mdbSonstigeWebsiteTitel')
        url = website.findtext('mdbSonstigeWebsiteURL')
        if type_.lower() == 'twitter':
            p.twitter_url = url
        if type_.lower() == 'facebook':
            p.facebook_url = url

    if doc.findtext('//mdbBundestagspraesident'):
        rx = Rolle()
        rx.person = p
        rx.funktion = u'Bundestagspräsident'
        db.session.add(rx)
    if doc.findtext('//mdbBundestagsvizepraesident'):
        rx = Rolle()
        rx.person = p
        rx.funktion = u'Bundestagsvizepräsident'
        db.session.add(rx)
    
    for n in doc.findall('//mdbObleuteGremium'):
        gremium = get_node_gremium(n)
        gremium.obleute.append(p)
    
    for n in doc.findall('//mdbVorsitzGremium'):
        gremium = get_node_gremium(n)
        gremium.vorsitz = p
    
    for n in doc.findall('//mdbStellvertretenderVorsitzGremium'):
        gremium = get_node_gremium(n)
        gremium.stellv_vorsitz = p
    
    for n in doc.findall('//mdbVorsitzSonstigesGremium'):
        gremium = get_node_gremium(n)
        gremium.vorsitz = p
    
    for n in doc.findall('//mdbStellvVorsitzSonstigesGremium'):
        gremium = get_node_gremium(n)
        gremium.stellv_vorsitz = p
    
    for n in doc.findall('//mdbOrdentlichesMitgliedGremium'):
        gremium = get_node_gremium(n)
        gremium.mitglieder.append(p)
    
    for n in doc.findall('//mdbStellvertretendesMitgliedGremium'):
        gremium = get_node_gremium(n)
        gremium.stellvertreter.append(p)
    
    for n in doc.findall('//mdbOrdentlichesMitgliedSonstigesGremium'):
        gremium = get_node_gremium(n)
        gremium.mitglieder.append(p)
    
    for n in doc.findall('//mdbStellvertretendesMitgliedSonstigesGremium'):
        gremium = get_node_gremium(n)
        gremium.stellvertreter.append(p)

    db.session.add(p)
    db.session.add(r)
    db.session.commit()


if __name__ == '__main__':
    load_index()

