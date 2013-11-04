# -*- coding: UTF-8 -*-
import logging
import re
import urllib
from lxml import etree
from urlparse import urljoin

import sqlaload as sl

from offenesparlament.core import app
from offenesparlament.data.lib.constants import FACTION_MAPS, \
    DIP_GREMIUM_TO_KEY, DIP_ABLAUF_STATES_FINISHED
from offenesparlament.data.lib.refresh import check_tags, Unmodified    
from offenesparlament.data.lib.retrieval import fetch, _html

EXTRAKT_INDEX = 'http://dipbt.bundestag.de/extrakt/ba/WP%s/'
INLINE_RE = re.compile(r"<!--(.*?)-->", re.M + re.S)
INLINE_COMMENTS_RE = re.compile(r"<-.*->", re.M + re.S)

log = logging.getLogger(__name__)


def inline_xml_from_page(page, url):
    try:
        for comment in INLINE_RE.findall(page):
            comment = comment.strip()
            if comment.startswith("<?xml"):
                comment = INLINE_COMMENTS_RE.sub('', comment).split('>', 1)[-1]
                comment = comment.decode('latin-1').replace('\x0b', ' ')
                try:
                    return etree.fromstring(comment)
                except Exception, e:
                    print [comment], url
                    log.exception(e)
    except Exception, e:
        log.exception(e)

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


def scrape_activity(engine, url, elem):
    urheber = elem.findtext("URHEBER")
    fundstelle = elem.findtext("FUNDSTELLE")
    Position = sl.get_table(engine, 'position')
    p = {'source_url': url, 
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
        sl.add_row(engine, Zuweisung, z)

    Beschluss = sl.get_table(engine, 'beschluss')
    for belem in elem.findall("BESCHLUSS"):
        b = pos_keys.copy()
        b['seite'] = belem.findtext("BESCHLUSSSEITE")
        b['dokument_text'] = belem.findtext("BEZUGSDOKUMENT")
        b['tenor'] = belem.findtext("BESCHLUSSTENOR")
        b['grundlage'] = belem.findtext("GRUNDLAGE")
        sl.add_row(engine, Beschluss, b)

    Referenz = sl.get_table(engine, 'referenz')
    try:
        dokument = dokument_by_url(p['fundstelle_url']) or \
            dokument_by_name(p['fundstelle'])
        dokument.update(pos_keys)
        sl.add_row(engine, Referenz, dokument)
    except Exception, e:
        log.exception(e)

    sl.add_row(engine, Position, p)
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
        b['ressort'] = belem.findtext("RESSORT")
        b['land'] = belem.findtext("BUNDESLAND")
        b['fraktion'] = FACTION_MAPS.get(belem.findtext("FRAKTION"), 
            belem.findtext("FRAKTION"))
        b['seite'] = belem.findtext("SEITE")
        b['art'] = belem.findtext("AKTIVITAETSART")
        sl.add_row(engine, Beitrag, b)

class NoContentException(Exception): pass

def scrape_ablauf(engine, url, force=False):
    Ablauf = sl.get_table(engine, 'ablauf')

    key = int(url.rsplit('/', 1)[-1].split('.')[0])
    a = sl.find_one(engine, Ablauf, source_url=url)
    if a is not None and a['abgeschlossen'] and not force:
        raise Unmodified()
    response = fetch(url)
    a = check_tags(a or {}, response, force)
    a.update({'key': key, 
              'source_url': url})
    doc = inline_xml_from_page(response.content, url)
    if doc is None: 
        raise NoContentException()
    
    a['wahlperiode'] = int(doc.findtext("WAHLPERIODE"))
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
    #a.schlagworte = []
    Schlagwort = sl.get_table(engine, 'schlagwort')
    for sw in doc.findall("SCHLAGWORT"):
        wort = {'wort': sw.text, 'source_url': url}
        sl.upsert(engine, Schlagwort, wort, unique=wort.keys())
    log.info("Ablauf %s: %s", url, a['titel'].encode('ascii', 'replace'))
    a['titel'] = a['titel'].strip().lstrip('.').strip()
    a = expand_dok_nr(a)
    a['abgeschlossen'] = DIP_ABLAUF_STATES_FINISHED.get(a['stand'], False)

    if a['wahlperiode'] != max(app.config.get('WAHLPERIODEN')):
        a['abgeschlossen'] = True

    if 'Originaltext der Frage(n):' in a['abstrakt']:
        _, a['abstrakt'] = a['abstrakt'].split('Originaltext der Frage(n):', 1)


    sl.delete(engine, sl.get_table(engine, 'position'), source_url=url)
    sl.delete(engine, sl.get_table(engine, 'beitrag'), source_url=url)
    sl.delete(engine, sl.get_table(engine, 'zuweisung'), source_url=url)
    sl.delete(engine, sl.get_table(engine, 'beschluss'), source_url=url)
    sl.delete(engine, sl.get_table(engine, 'referenz'), source_url=url)

    for elem in doc.findall(".//VORGANGSPOSITION"):
        scrape_activity(engine, url, elem)

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
        dokument['source_url'] = url
        sl.upsert(engine, Referenz, dokument, unique=[
            'link', 'source_url', 'seiten'
            ])

    for elem in doc.findall("PLENUM"):
        link = elem.findtext("PLPR_LINK")
        if link is not None and '#' in link:
            link, hash = link.rsplit('#', 1)
        dokument = dokument_by_id(elem.findtext("PLPR_HERAUSGEBER"), 
                'plpr', elem.findtext("PLPR_NUMMER"), link=link)
        dokument['text'] = elem.findtext("PLPR_KLARTEXT")
        dokument['seiten'] = elem.findtext("PLPR_SEITEN")
        dokument['source_url'] = url
        sl.upsert(engine, Referenz, dokument, unique=[
            'link', 'source_url', 'seiten'
            ])

    sl.upsert(engine, Ablauf, a, unique=['source_url'])
    return a


def scrape_index():
    for wp in app.config.get('WAHLPERIODEN'):
        index_url = EXTRAKT_INDEX % wp
        response, doc = _html(index_url, timeout=120.0)
        for result in doc.findall("//a[@class='linkIntern']"):
            yield urljoin(index_url, result.get('href'))

