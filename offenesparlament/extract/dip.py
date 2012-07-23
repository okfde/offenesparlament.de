# -*- coding: UTF-8 -*-
import logging
import re
import urllib
import time
import requests
from lxml import etree
from itertools import count
from urlparse import urlparse, urljoin, parse_qs
from StringIO import StringIO

import sqlaload as sl

from offenesparlament.extract.util import threaded
from offenesparlament.load.fetch import UA, _html, fetch
from offenesparlament.core import etl_engine

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARN)

MAKE_SESSION_URL = "http://dipbt.bundestag.de/dip21.web/bt"
BASE_URL = "http://dipbt.bundestag.de/dip21.web/searchProcedures/simple_search.do?method=Suchen&offset=%s&anzahl=100"
ABLAUF_URL = "http://dipbt.bundestag.de/dip21.web/searchProcedures/simple_search_list.do?selId=%s&method=select&offset=100&anzahl=100&sort=3&direction=desc"
DETAIL_VP_URL = "http://dipbt.bundestag.de/dip21.web/searchProcedures/simple_search_detail_vp.do?vorgangId=%s"    

FACTION_MAPS = {
        u"BÜNDNIS 90/DIE GRÜNEN": u"B90/Die Grünen",
        u"DIE LINKE.": u"Die LINKE.",
        u"Bündnis 90/Die Grünen": u"B90/Die Grünen",
        u"Die Linke": "Die LINKE."
        }

DIP_GREMIUM_TO_KEY = {
    u"Ausschuss für Bildung, Forschung und Technikfolgenabschätzung": "a18",
    u"Ausschuss für Ernährung, Landwirtschaft und Verbraucherschutz": "a10",
    u"Ausschuss für Tourismus": "a20",
    u"Ausschuss für Umwelt, Naturschutz und Reaktorsicherheit": "a16",
    u"Ausschuss für Verkehr, Bau und Stadtentwicklung": "a15",
    u"Ausschuss für Arbeit und Soziales": "a11",
    u"Ausschuss für Familie, Senioren, Frauen und Jugend": "a13",
    u"Ausschuss für Wirtschaft und Technologie": "a09",
    u"Finanzausschuss": "a07",
    u"Haushaltsausschuss": "a08",
    u"Ausschuss für die Angelegenheiten der Europäischen Union": "a21",
    u"Ausschuss für Agrarpolitik und Verbraucherschutz": "a10",
    u"Ausschuss für Innere Angelegenheiten": "a04",
    u"Wirtschaftsausschuss": "a09",
    u"Ausschuss für Gesundheit": "a14",
    u"Ausschuss für Wahlprüfung, Immunität und Geschäftsordnung": "a01",
    u"Rechtsausschuss": "a06",
    u"Ausschuss für Fragen der Europäischen Union": "a21",
    u"Ausschuss für Kulturfragen": "a22",
    u"Gesundheitsausschuss": "a14",
    u"Ausschuss für Menschenrechte und humanitäre Hilfe": "a17",
    u"Ausschuss für wirtschaftliche Zusammenarbeit und Entwicklung": "a19",
    u"Ausschuss für Auswärtige Angelegenheiten": "a03",
    u"Ausschuss für Kultur und Medien": "a22",
    u"Sportausschuss": "a05",
    u"Auswärtiger Ausschuss": "a03",
    u"Ausschuss für Arbeit und Sozialpolitik": "a11",
    u"Ausschuss für Frauen und Jugend": "a13",
    u"Ausschuss für Städtebau, Wohnungswesen und Raumordnung": "a15",
    u"Innenausschuss": "a04",
    u"Verkehrsausschuss": "a15",
    u"Verteidigungsausschuss": "a12",
    u"Ausschuss für Familie und Senioren": "a13",
    u"Petitionsausschuss": "a02",
    u"Ausschuss für Verteidigung": "a12",
    u"Ältestenrat": "002"
    }


DIP_ABLAUF_STATES_FINISHED = { 
    u'Beantwortet': True,
    u'Abgeschlossen': True,
    u'Abgelehnt': True,
    u'In der Beratung (Einzelheiten siehe Vorgangsablauf)': False,
    u'Verkündet': True,
    u'Angenommen': True,
    u'Keine parlamentarische Behandlung': False,
    u'Überwiesen': False,
    u'Beschlussempfehlung liegt vor': False,
    u'Noch nicht beraten': False,
    u'Für erledigt erklärt': True,
    u'Noch nicht beantwortet': False,
    u'Zurückgezogen': True,
    u'Dem Bundestag zugeleitet - Noch nicht beraten': False,
    u'Nicht beantwortet wegen Nichtanwesenheit des Fragestellers': True,
    u'Zustimmung erteilt': True,
    u'Keine parlamentarische Behandlung': True,
    u'Aufhebung nicht verlangt': False,
    u'Den Ausschüssen zugewiesen': False,
    u'Zusammengeführt mit... (siehe Vorgangsablauf)': True,
    u'Dem Bundesrat zugeleitet - Noch nicht beraten': False,
    u'Zustimmung (mit Änderungen) erteilt': True,
    u'Bundesrat hat Vermittlungsausschuss nicht angerufen': False,
    u'Bundesrat hat zugestimmt': False,
    u'1. Durchgang im Bundesrat abgeschlossen': False,
    u'Einbringung abgelehnt': True,
    u'Verabschiedet': True,
    u'Entlastung erteilt': True,
    u'Abschlussbericht liegt vor': True,
    u'Erledigt durch Ende der Wahlperiode (§ 125 GOBT)': True,
    u'Zuleitung beschlossen': False,
    u'Zuleitung in geänderter Fassung beschlossen': False,
    u'Für gegenstandslos erklärt': False,
    u'Nicht ausgefertigt wegen Zustimmungsverweigerung des Bundespräsidenten': False,
    u'Im Vermittlungsverfahren': False,
    u'Zustimmung versagt': True,
    u'Einbringung in geänderter Fassung beschlossen': False,
    u'Bundesrat hat keinen Einspruch eingelegt': False,
    u'Bundesrat hat Einspruch eingelegt': False,
    u'Zuleitung in Neufassung beschlossen': True,
    u'Untersuchungsausschuss eingesetzt': False
}


inline_re = re.compile(r"<!--(.*?)-->", re.M + re.S)
inline_comments_re = re.compile(r"<-.*->", re.M + re.S)

def inline_xml_from_page(page):
    for comment in inline_re.findall(page):
        comment = comment.strip()
        if comment.startswith("<?xml"):
            comment = inline_comments_re.sub('', comment).split('>', 1)[-1]
            comment = comment.decode('latin-1')
            return etree.fromstring(comment)

def _get_dokument(hrsg, typ, nummer, link=None):
    nummer = nummer.lstrip("0")
    return {'link': link, 'hrsg': hrsg, 
            'typ': typ, 'nummer': nummer}

def dokument_by_id(hrsg, typ, nummer, link=None):
    if '/' in nummer:
        section, nummer = nummer.split("/", 1)
        nummer = nummer.lstrip("0")
        nummer = section + "/" + nummer
    return _get_dokument(hrsg, typ, nummer, link=link)

def dokument_by_url(url):
    if url is None or not url:
        return
    if '#' in url:
        url, fragment = url.split('#', 1)
    name, file_ext = url.rsplit('.', 1)
    base = name.split('/', 4)[-1].split("/")
    hrsg, typ = {"btd": ("BT", "drs"),
                 "btp": ("BT", "plpr"),
                 "brd": ("BR", "drs"),
                 "brp": ("BR", "plpr")
                }.get(base[0])
    if hrsg == 'BR' and typ == 'plpr': 
        nummer = base[1]
    elif hrsg == 'BR' and typ == 'drs':
        nummer = "/".join(base[-1].split("-"))
    elif hrsg == 'BT':
        s = base[1]
        nummer = base[-1][len(s):].lstrip("0")
        nummer = s + "/" + nummer
    return _get_dokument(hrsg, typ, nummer, link=url)


END_ID = re.compile("[,\n]")
def dokument_by_name(name):
    if name is None or not name:
        return
    if ' - ' in name:
        date, name = name.split(" - ", 1)
    else:
        log.warn("NO DATE: %s", name)
    if ',' in name or '\n' in name:
        name, remainder = END_ID.split(name, 1)
    typ, nummer = name.strip().split(" ", 1)
    hrsg, typ = {
            "BT-Plenarprotokoll": ("BT", "plpr"), 
            "BT-Drucksache": ("BT", "drs"), 
            "BR-Plenarprotokoll": ("BR", "plpr"),
            "BR-Drucksache": ("BR", "drs")
            }.get(typ, ('BT', 'drs'))
    link = None
    if hrsg == 'BT' and typ == 'drs':
        print [nummer]
        f, s = nummer.split("/", 1)
        s = s.split(" ")[0]
        s = s.zfill(5)
        link = "http://dipbt.bundestag.de:80/dip21/btd/%s/%s/%s%s.pdf" % (f, s[:3], f, s)
    return _get_dokument(hrsg, typ, nummer, link=link)


# EU Links
COM_LINK = re.compile('.*Kom.\s\((\d{1,4})\)\s(\d{1,6}).*')
SEC_LINK = re.compile('.*Sek.\s\((\d{1,4})\)\s(\d{1,6}).*')
RAT_LINK = re.compile('.*Ratsdok.\s*([\d\/]*).*')
EUR_LEX_RECH = "http://eur-lex.europa.eu/Result.do?T1=%s&T2=%s&T3=%s&RechType=RECH_naturel"
LEX_URI = "http://eur-lex.europa.eu/LexUriServ/LexUriServ.do?uri=%s:%s:%s:FIN:DE:%s"
CONS = "http://register.consilium.europa.eu/servlet/driver?lang=DE&typ=Advanced&cmsid=639&ff_COTE_DOCUMENT=%s&fc=REGAISDE&md=100&rc=1&nr=1&page=Detail"
def expand_dok_nr(ablauf):
    if ablauf['eu_dok_nr']:
        com_match = COM_LINK.match(ablauf['eu_dok_nr'])
        if com_match:
            year, process = com_match.groups()
            ablauf['eur_lex_url'] = EUR_LEX_RECH % ("V5", year, process)
            ablauf['eur_lex_pdf'] = LEX_URI % ("COM", year, process.zfill(4), "PDF")
        sec_match = SEC_LINK.match(ablauf['eu_dok_nr'])
        if sec_match:
            year, process = sec_match.groups()
            ablauf['eur_lex_url'] = EUR_LEX_RECH % ("V7", year, process)
            ablauf['eur_lex_pdf'] = LEX_URI % ("SEC", year, process.zfill(4), "PDF")
        rat_match = RAT_LINK.match(ablauf['eu_dok_nr'])
        if rat_match:
            id, = rat_match.groups()
            ablauf['consilium_url'] = CONS % urllib.quote(id)
    return ablauf


def scrape_activities(ablauf, doc, engine):
    if doc is not None: 
        for elem in doc.findall(".//VORGANGSPOSITION"):
            scrape_activity(ablauf, elem, engine)

def scrape_activity(ablauf, elem, engine):
    urheber = elem.findtext("URHEBER")
    fundstelle = elem.findtext("FUNDSTELLE")
    Position = sl.get_table(engine, 'position')
    p = sl.find_one(engine, Position, 
                    urheber=urheber, 
                    fundstelle=fundstelle, 
                    ablauf_id=ablauf['ablauf_id'])
    if p is not None:
        return 
    p = {'ablauf_id': ablauf['ablauf_id'], 
         'urheber': urheber,
         'fundstelle': fundstelle}
    pos_keys = p.copy()
    p['zuordnung'] = elem.findtext("ZUORDNUNG")
    p['abstrakt'] = elem.findtext("VP_ABSTRAKT")
    p['fundstelle_url'] = elem.findtext("FUNDSTELLE_LINK")
    
    Zuweisung = sl.get_table(engine, 'zuweisung')
    for zelem in elem.findall("ZUWEISUNG"):
        z = pos_keys.copy()
        z['text'] = zelem.findtext("AUSSCHUSS_KLARTEXT")
        z['federfuehrung'] = zelem.find("FEDERFUEHRUNG") is not None
        z['gremium_key'] = DIP_GREMIUM_TO_KEY.get(z['text'])
        sl.upsert(engine, Zuweisung, z, unique=[])
        
    Beschluss = sl.get_table(engine, 'beschluss')
    for belem in elem.findall("BESCHLUSS"):
        b = pos_keys.copy()
        b['seite'] = belem.findtext("BESCHLUSSSEITE")
        b['dokument_text'] = belem.findtext("BEZUGSDOKUMENT")
        b['tenor'] = belem.findtext("BESCHLUSSTENOR")
        b['grundlage'] = belem.findtext("GRUNDLAGE")
        sl.upsert(engine, Beschluss, b, unique=[])

    Referenz = sl.get_table(engine, 'referenz')
    try:
        dokument = dokument_by_url(p['fundstelle_url']) or \
            dokument_by_name(p['fundstelle'])
        dokument.update(pos_keys)
        dokument['ablauf_key'] = ablauf['key']
        dokument['wahlperiode'] = ablauf['wahlperiode']
        sl.upsert(engine, Referenz, dokument, unique=[
                'link', 'wahlperiode', 'ablauf_key', 'seiten'
                ])
    except Exception, e:
        log.exception(e)

    sl.upsert(engine, Position, p, unique=[])
    Person = sl.get_table(engine, 'person')
    Beitrag = sl.get_table(engine, 'beitrag')
    for belem in elem.findall("PERSOENLICHER_URHEBER"):
        b = pos_keys.copy()
        b['vorname'] = belem.findtext("VORNAME")
        b['nachname'] = belem.findtext("NACHNAME")
        b['funktion'] = belem.findtext("FUNKTION")
        b['ort'] = belem.findtext('WAHLKREISZUSATZ')
        p = sl.find_one(engine, Person, 
                vorname=b['vorname'],
                nachname=b['nachname'],
                ort=b['ort'])
        if p is not None:
            b['person_source_url'] = p['source_url']
        #q = Rolle.query.filter_by(funktion=funktion)
        #r = q.filter_by(person_id=p.id).first()
        #if r is None:
        #    r = Rolle()
        #    r.funktion = funktion
        b['ressort'] = belem.findtext("RESSORT")
        b['land'] = belem.findtext("BUNDESLAND")
        b['fraktion'] = FACTION_MAPS.get(belem.findtext("FRAKTION"), 
            belem.findtext("FRAKTION"))
        #    r.person = ps
        #    db.session.add(r)

        b['seite'] = belem.findtext("SEITE")
        b['art'] = belem.findtext("AKTIVITAETSART")
        sl.upsert(engine, Beitrag, b, unique=[])

class TooFarInThePastException(Exception): pass

class NoContentException(Exception): pass

#from threading import local
#tl = local()
def scrape_ablauf(url, engine, wahlperiode=17):
    wahlperiode = str(wahlperiode)
    #if not hasattr(tl, 'engine'):
    #    tl.engine = etl_engine()
    #engine = tl.engine
    Ablauf = sl.get_table(engine, 'ablauf')

    key = url.rsplit('/', 1)[-1].split('.')[0]
    a = sl.find_one(engine, Ablauf, key=key, 
                    bt_wahlperiode=wahlperiode)
    if a is not None and a['abgeschlossen']:
        log.info("SKIPPING: %s", a['titel'])
        return
    if a is None:
        a = {}
    a['key'] = key
    doc = inline_xml_from_page(fetch(url))
    if doc is None: 
        raise NoContentException()
    
    a['wahlperiode'] = wahlperiode
    a['bt_wahlperiode'] = wahlperiode
    if doc.findtext("WAHLPERIODE"):
        wahlperiode != doc.findtext("WAHLPERIODE")
    
    a['ablauf_id'] = "%s/%s" % (wahlperiode, key)
    a['typ'] = doc.findtext("VORGANGSTYP")
    a['titel'] = doc.findtext("TITEL")

    if not a['titel'] or not len(a['titel'].strip()):
        raise NoContentException()

    if '\n' in a['titel']:
        t, k = a['titel'].rsplit('\n', 1)
        k = k.strip()
        if k.startswith('KOM') or k.startswith('SEK'):
            a['titel'] = t

    a['initiative'] = doc.findtext("INITIATIVE")
    a['stand'] = doc.findtext("AKTUELLER_STAND")
    a['signatur'] = doc.findtext("SIGNATUR")
    a['gesta_id'] = doc.findtext("GESTA_ORDNUNGSNUMMER")
    a['eu_dok_nr'] = doc.findtext("EU_DOK_NR")
    a['abstrakt'] = doc.findtext("ABSTRAKT")
    a['sachgebiet'] = doc.findtext("SACHGEBIET")
    a['zustimmungsbeduerftig'] = doc.findtext("ZUSTIMMUNGSBEDUERFTIGKEIT")
    a['source_url'] = url
    #a.schlagworte = []
    Schlagwort = sl.get_table(engine, 'schlagwort')
    for sw in doc.findall("SCHLAGWORT"):
        wort = {'wort': sw.text, 'key': key, 'wahlperiode': wahlperiode}
        sl.upsert(engine, Schlagwort, wort, unique=wort.keys())
    log.info("Ablauf %s: %s",key, a['titel'])
    a['titel'] = a['titel'].strip().lstrip('.').strip()
    a = expand_dok_nr(a)
    a['abgeschlossen'] = DIP_ABLAUF_STATES_FINISHED.get(a['stand'], False)
    if 'Originaltext der Frage(n):' in a['abstrakt']:
        _, a['abstrakt'] = a['abstrakt'].split('Originaltext der Frage(n):', 1)

    Referenz = sl.get_table(engine, 'referenz')
    for elem in doc.findall("WICHTIGE_DRUCKSACHE"):
        link = elem.findtext("DRS_LINK")
        hash = None
        if link is not None and '#' in link:
            link, hash = link.rsplit('#', 1)
        dokument = dokument_by_id(elem.findtext("DRS_HERAUSGEBER"), 
                'drs', elem.findtext("DRS_NUMMER"), link=link)
        dokument['text'] = elem.findtext("DRS_TYP")
        dokument['seiten'] = hash
        dokument['wahlperiode'] = wahlperiode
        dokument['ablauf_key'] = key
        sl.upsert(engine, Referenz, dokument, unique=[
            'link', 'wahlperiode', 'ablauf_key', 'seiten'
            ])

    for elem in doc.findall("PLENUM"):
        link = elem.findtext("PLPR_LINK")
        if link is not None and '#' in link:
            link, hash = link.rsplit('#', 1)
        dokument = dokument_by_id(elem.findtext("PLPR_HERAUSGEBER"), 
                'plpr', elem.findtext("PLPR_NUMMER"), link=link)
        dokument['text'] = elem.findtext("PLPR_KLARTEXT")
        dokument['seiten'] = elem.findtext("PLPR_SEITEN")
        dokument['wahlperiode'] = wahlperiode
        dokument['ablauf_key'] = key
        sl.upsert(engine, Referenz, dokument, unique=[
            'link', 'wahlperiode', 'ablauf_key', 'seiten'
            ])

    sl.upsert(engine, Ablauf, a, unique=['key', 'wahlperiode'])
    scrape_activities(a, doc, engine)
    engine.dispose()

def load_dip(engine):
    def bound_scrape(url):
        scrape_ablauf(url, engine)
    threaded(load_dip_index(), bound_scrape, num_threads=5)

EXTRAKT_INDEX = 'http://dipbt.bundestag.de/extrakt/ba/WP17/'

def load_dip_index():
    doc = _html(EXTRAKT_INDEX, timeout=120.0)
    for result in doc.findall("//a[@class='linkIntern']"):
        yield urljoin(EXTRAKT_INDEX, result.get('href'))

if __name__ == '__main__':
    engine = etl_engine()
    print "DESTINATION", engine
    load_dip(engine)

