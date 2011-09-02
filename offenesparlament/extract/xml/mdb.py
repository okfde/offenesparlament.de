#coding: utf-8
import logging
import sys
from lxml import etree
from datetime import datetime

from webstore.client import URL as WebStore

MDB_INDEX_URL = "http://www.bundestag.de/xml/mdb/index.xml"

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.NOTSET)

def add_to_gremium(node, url, role, db):
    key = node.get('id')
    table = db['gremium']
    g = table.find_one(key=key)
    if g is None:
        g = {'key': key, 'type': 'sonstiges'}
        g['name'] = node.findtext('gremiumName')
        g['url'] = node.findtext('gremiumURL')
        table.writerow(g, unique_columns=['key'])
    db['gremium_mitglieder'].writerow({
        'gremium_key': g['key'],
        'person_source_url': url,
        'role': role
        }, unique_columns=['person_source_url', 'gremium_key', 'role'])

def load_index(db): 
    doc = etree.parse(MDB_INDEX_URL)
    for info_url in doc.findall("//mdbInfoXMLURL"):
        load_mdb(info_url.text, db)

def load_mdb(url, db):
    doc = etree.parse(url)
    id = int(doc.findtext('//mdbID'))
    table_person = db['person']
    table_rolle = db['rolle']
    p = table_person.find_one(mdb_id=id)
    r = {'person_source_url': url, 
         'funktion': 'MdB'}
    if p is None:
        p = {'source_url': url}
    else:
        r_ = table_rolle.find_one(mdb_id=id, funktion='MdB')
        if r_ is not None:
            r = r_

    r['mdb_id'] = p['mdb_id'] = id
    r['status'] = doc.find('//mdbID').get('status')
    if doc.findtext('//mdbAustrittsdatum'):
        r['austritt'] = datetime.strptime(doc.findtext('//mdbAustrittsdatum'),
                                       '%d.%m.%Y').isoformat()
    p['vorname'] = doc.findtext('//mdbVorname')
    p['nachname'] = doc.findtext('//mdbZuname')
    p['adelstitel'] = doc.findtext('//mdbAdelstitel')
    p['titel'] = doc.findtext('//mdbAkademischerTitel')
    p['ort'] = doc.findtext('//mdbOrtszusatz')
    log.info('MdB: %s %s (%s)' % (p['vorname'], p['nachname'], p['ort']))
    p['geburtsdatum'] = doc.findtext('//mdbGeburtsdatum')
    p['religion'] = doc.findtext('//mdbReligionKonfession')
    p['hochschule'] = doc.findtext('//mdbHochschulbildung')
    p['beruf'] = doc.findtext('//mdbBeruf')
    p['berufsfeld'] = doc.find('//mdbBeruf').get('berufsfeld')
    p['geschlecht'] = doc.findtext('//mdbGeschlecht')
    p['familienstand'] = doc.findtext('//mdbFamilienstand')
    p['kinder'] = doc.findtext('//mdbAnzahlKinder')
    r['fraktion'] = doc.findtext('//mdbFraktion')
    p['fraktion'] = doc.findtext('//mdbFraktion')
    p['partei'] = doc.findtext('//mdbPartei')
    p['land'] = doc.findtext('//mdbLand')
    r['gewaehlt'] = doc.findtext('//mdbGewaehlt')
    p['bio_url'] = doc.findtext('//mdbBioURL')
    p['bio'] = doc.findtext('//mdbBiografischeInformationen')
    p['wissenswertes'] = doc.findtext('//mdbWissenswertes')
    p['homepage_url'] = doc.findtext('//mdbHomepageURL')
    p['telefon'] = doc.findtext('//mdbTelefon')
    p['angaben'] = doc.findtext('//mdbVeroeffentlichungspflichtigeAngaben')
    p['foto_url'] = doc.findtext('//mdbFotoURL')
    p['foto_copyright'] = doc.findtext('//mdbFotoCopyright')
    p['reden_plenum_url'] = doc.findtext('//mdbRedenVorPlenumURL')
    p['reden_plenum_rss_url'] = doc.findtext('//mdbRedenVorPlenumRSS')
    
    p['wk_nummer'] = doc.findtext('//mdbWahlkreisNummer')
    p['wk_name'] = doc.findtext('//mdbWahlkreisName') 
    p['wk_url'] = doc.findtext('//mdbWahlkreisURL')

    for website in doc.findall('//mdbSonstigeWebsite'):
        type_ = website.findtext('mdbSonstigeWebsiteTitel')
        ws_url = website.findtext('mdbSonstigeWebsiteURL')
        if type_.lower() == 'twitter':
            p['twitter_url'] = ws_url
        if type_.lower() == 'facebook':
            p['facebook_url'] = ws_url

    if doc.findtext('//mdbBundestagspraesident'):
        table_rolle.writerow({
            'person_source_url': url, 
            'funktion': u'Bundestagspräsident',
            }, 
            unique_columns=['person_source_url', 'funktion'])
    if doc.findtext('//mdbBundestagsvizepraesident'):
        table_rolle.writerow({
            'person_source_url': url, 
            'funktion': u'Bundestagsvizepräsident',
            }, 
            unique_columns=['person_source_url', 'funktion'])
    
    for n in doc.findall('//mdbObleuteGremium'):
        add_to_gremium(n, url, 'obleute', db)
    
    for n in doc.findall('//mdbVorsitzGremium'):
        add_to_gremium(n, url, 'vorsitz', db)
    
    for n in doc.findall('//mdbStellvertretenderVorsitzGremium'):
        add_to_gremium(n, url, 'stellv_vorsitz', db)
    
    for n in doc.findall('//mdbVorsitzSonstigesGremium'):
        add_to_gremium(n, url, 'vorsitz', db)
    
    for n in doc.findall('//mdbStellvVorsitzSonstigesGremium'):
        add_to_gremium(n, url, 'stellv_vorsitz', db)
    
    for n in doc.findall('//mdbOrdentlichesMitgliedGremium'):
        add_to_gremium(n, url, 'mitglied', db)
    
    for n in doc.findall('//mdbStellvertretendesMitgliedGremium'):
        add_to_gremium(n, url, 'stellv_mitglied', db)
    
    for n in doc.findall('//mdbOrdentlichesMitgliedSonstigesGremium'):
        add_to_gremium(n, url, 'mitglied', db)
    
    for n in doc.findall('//mdbStellvertretendesMitgliedSonstigesGremium'):
        add_to_gremium(n, url, 'stellv_mitglied', db)
    
    table_person.writerow(p, unique_columns=['source_url'])
    table_rolle.writerow(r, unique_columns=['person_source_url', 'funktion'])

if __name__ == '__main__':
    assert len(sys.argv)==2, "Need argument: webstore-url!"
    db, _ = WebStore(sys.argv[1])
    print "DESTINATION", db
    load_index(db)

