# -*- coding: UTF-8 -*-
from offenesparlament.core import db
from offenesparlament.model import Ablauf, Schlagwort
from offenesparlament.model import Dokument, Referenz
from offenesparlament.model import Position, Zuweisung
from offenesparlament.model import Gremium, Beschluss
from offenesparlament.model import Beitrag, Person, Rolle
import logging
import re, string
import urllib2, urllib
import cookielib
from datetime import datetime
from hashlib import sha1
from threading import Lock 
from lxml import etree
from pprint import pprint
from itertools import count
from urlparse import urlparse, urljoin, parse_qs
from StringIO import StringIO

log = logging.getLogger(__name__)

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

jar = None
lock = Lock()

inline_re = re.compile(r"<!--(.*?)-->", re.M + re.S)
inline_comments_re = re.compile(r"<-.*->", re.M + re.S)

def inline_xml_from_page(page):
    for comment in inline_re.findall(page):
        comment = comment.strip()
        if comment.startswith("<?xml"):
            comment = inline_comments_re.sub('', comment)
            return etree.parse(StringIO(comment))

def get_dip_with_cookie(url, method='GET', data={}):
    class _Request(urllib2.Request):
        def get_method(self): 
            return method
    
    lock.acquire()
    try:
        def _req(url, jar, data={}):
            _data = urllib.urlencode(data) 
            req = _Request(url, _data)
            jar.add_cookie_header(req)
            fp = urllib2.urlopen(req)
            jar.extract_cookies(fp, req)
            return fp
        global jar
        if jar is None:
            jar = cookielib.CookieJar()
            fp = _req(MAKE_SESSION_URL, jar)
            fp.read()
            fp.close()
        return _req(url, jar, data=data)
    finally:
        lock.release()


def _get_dokument(hrsg, typ, nummer, link=None):
    nummer = nummer.lstrip("0")
    q = Dokument.query.filter_by(hrsg=hrsg)
    q = q.filter_by(typ=typ).filter_by(nummer=nummer)
    dokument = q.first()
    if dokument is None:
        dokument = Dokument()
    dokument.hrsg = hrsg
    dokument.typ = typ
    dokument.nummer = nummer
    if link is not None:
        dokument.link = link
    db.session.add(dokument)
    return dokument

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
        log.warn("NO DATE: %s" % name)
    if ',' in name or '\n' in name:
        name, remainder = END_ID.split(name, 1)
    typ, nummer = name.strip().split(" ")
    hrsg, typ = {
            "BT-Plenarprotokoll": ("BT", "plpr"), 
            "BT-Drucksache": ("BT", "drs"), 
            "BR-Plenarprotokoll": ("BR", "plpr"),
            "BR-Drucksache": ("BR", "drs")
            }.get(typ)
    if hrsg == 'BT' and typ == 'drs':
        f, s = nummer.split("/")
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
    if ablauf.eu_dok_nr:
        com_match = COM_LINK.match(ablauf.eu_dok_nr)
        if com_match:
            year, process = com_match.groups()
            ablauf.eur_lex_url = EUR_LEX_RECH % ("V5", year, process)
            ablauf.eur_lex_pdf = LEX_URI % ("COM", year, process.zfill(4), "PDF")
        sec_match = SEC_LINK.match(ablauf.eu_dok_nr)
        if sec_match:
            year, process = sec_match.groups()
            ablauf.eur_lex_url = EUR_LEX_RECH % ("V7", year, process)
            ablauf.eur_lex_pdf = LEX_URI % ("SEC", year, process.zfill(4), "PDF")
        rat_match = RAT_LINK.match(ablauf.eu_dok_nr)
        if rat_match:
            id, = rat_match.groups()
            ablauf.consilium_url = CONS % urllib.quote(id)
    return ablauf


def activity_person_merge(db, akteur):
    akteur = akteur.copy()

    if akteur.get('vorname') == 'Wolfgang' and akteur.get('zuname') == 'Neskovic':
        akteur['zuname'] = u'Nešković'
    if akteur.get('vorname') == 'Eva' and akteur.get('zuname') == 'Klamt':
        akteur['vorname'] = 'Ewa'
    if akteur.get('vorname') == 'Daniela' and akteur.get('zuname') == 'Raab':
        # data mining and marriage: not a good fit. 
        akteur['zuname'] = 'Ludwig'
    candidates = list(db.akteur.find(
        {"vorname": akteur.get('vorname'), 
         "zuname": akteur.get('zuname')}))
    if len(candidates) == 0:
        candidates = list(db.akteur.find(
            {"vorname": {"$regex": akteur.get('vorname') + ".*"}, 
             "zuname": akteur.get('zuname')}))
    if akteur.get('funktion') == 'MdB' or len(candidates) == 1:
        if len(candidates) == 0:
            def _namesub(name): 
                s = '.*'
                for c in name:
                    if c in string.letters:
                        s += c
                    else:
                        s += '.'
                return s + '.*'
            candidates = list(db.akteur.find(
                {"vorname": {"$regex": _namesub(akteur.get('vorname'))}, 
                 "zuname": {"$regex": _namesub(akteur.get('zuname'))}}))
        if len(candidates) == 0:
            candidates = list(db.akteur.find({"$or": [
                {"vorname": akteur.get('vorname')}, 
                {"zuname": akteur.get('zuname')}]}))
        if len(candidates) == 1:
            a = candidates[0]
            db.akteur.update({'_id': a.get('_id')},
                {"$set": {"funktion": akteur.get("funktion"),
                          "ressort": akteur.get("ressort"),
                          "ortszusatz": akteur.get("ortszusatz"),
                          "state": akteur.get("state")}})
            return a.get('_id')
        pprint(akteur)
        print "HAS", len(candidates), "CANDIDATES"
        pprint(candidates)
        return None
    a = akteur.copy()
    if 'seite' in a: 
        del a['seite']
    if 'aktivitaet' in a:
        del a['aktivitaet']
    a['key'] = sha1(repr(a).encode("ascii", "ignore")).hexdigest()[:10]
    db.akteur.update({"key": a['key']}, a, upsert=True)
    return db.akteur.find_one({"key": a['key']}).get('_id')


def scrape_activities(ablauf):
    urlfp = get_dip_with_cookie(DETAIL_VP_URL % ablauf.key)
    xml = inline_xml_from_page(urlfp.read())
    urlfp.close()
    if xml is not None: 
        for elem in xml.findall(".//VORGANGSPOSITION"):
            scrape_activity(ablauf, elem)

def scrape_activity(ablauf, elem):
    urheber = elem.findtext("URHEBER")
    fundstelle = elem.findtext("FUNDSTELLE")
    q = Position.query.filter_by(urheber=urheber)
    q = q.filter_by(ablauf_id=ablauf.id)
    p = q.filter_by(fundstelle=fundstelle).first()
    if p is not None:
        return 
    p = Position()
    p.ablauf = ablauf
    p.urheber = urheber
    p.fundstelle = fundstelle
    p.zuordnung = elem.findtext("ZUORDNUNG")
    p.fundstelle_url = elem.findtext("FUNDSTELLE_LINK")
    
    dt, rest = p.fundstelle.split("-", 1)
    p.date = datetime.strptime(dt.strip(), "%d.%m.%Y")
    if ',' in p.urheber:
        typ, quelle = p.urheber.split(',', 1)
        p.quelle = re.sub("^.*Urheber.*:", "", quelle).strip()
        p.typ = typ.strip()
    db.session.add(p)
    
    for zelem in elem.findall("ZUWEISUNG"):
        z = Zuweisung()
        z.position = p
        z.text = zelem.findtext("AUSSCHUSS_KLARTEXT")
        z.federfuehrung = zelem.find("FEDERFUEHRUNG") is not None
        gremium_key = DIP_GREMIUM_TO_KEY.get(z.text)
        g = Gremium.query.filter_by(key=gremium_key).first()
        if g is None:
            log.warn("TODO: %s" % z.text)
        z.gremium = g
        db.session.add(z)
    
    for belem in elem.findall("BESCHLUSS"):
        b = Beschluss()
        b.position = p
        b.seite = belem.findtext("BESCHLUSSSEITE")
        b.dokument_text = belem.findtext("BEZUGSDOKUMENT")
        b.tenor = belem.findtext("BESCHLUSSTENOR")
        db.session.add(b)
    
    p.dokument = dokument_by_url(p.fundstelle_url) or \
        dokument_by_name(p.fundstelle)
    
    for belem in elem.findall("PERSOENLICHER_URHEBER"):
        vorname = belem.findtext("VORNAME")
        nachname = belem.findtext("NACHNAME")
        funktion = belem.findtext("FUNKTION")
        ortszusatz = belem.findtext('WAHLKREISZUSATZ')
        q = Person.query.filter_by(vorname=vorname)
        q = q.filter_by(nachname=nachname)
        ps = q.filter_by(ort=ortszusatz).first()
        if ps is None:
            ps = Person()
            ps.vorname = vorname
            ps.nachname = nachname
            ps.ort = ortszusatz
            db.session.add(ps)
        q = Rolle.query.filter_by(funktion=funktion)
        r = q.filter_by(person_id=p.id).first()
        if r is None:
            r = Rolle()
            r.funktion = funktion
            r.ressort = belem.findtext("RESSORT")
            r.land = belem.findtext("BUNDESLAND")
            r.fraktion = FACTION_MAPS.get(belem.findtext("FRAKTION"), 
                belem.findtext("FRAKTION"))
            r.person = ps
            db.session.add(r)

        b = Beitrag()
        b.seite = belem.findtext("SEITE")
        b.art = belem.findtext("AKTIVITAETSART")
        b.position = p
        b.person = ps
        b.rolle = r
        db.session.add(b)

def scrape_ablauf(url):
    a = Ablauf.query.filter_by(source_url=url).first()
    if a is not None and a.abgeschlossen:
        log.info("Skipping: %s" % a.titel)
        return
    if a is None:
        a = Ablauf()
    a.key = parse_qs(urlparse(url).query).get('selId')[0]
    urlfp = get_dip_with_cookie(url)
    doc = inline_xml_from_page(urlfp.read())
    urlfp.close()
    if doc is None: 
        log.warn("Could not find embedded XML in Ablauf: %s", a.key)
        return
    a.wahlperiode = doc.findtext("WAHLPERIODE")
    a.typ = doc.findtext("VORGANGSTYP")
    a.titel = doc.findtext("TITEL")
    a.initiative = doc.findtext("INITIATIVE")
    a.stand = doc.findtext("AKTUELLER_STAND")
    a.signatur = doc.findtext("SIGNATUR")
    a.gesta_id = doc.findtext("GESTA_ORDNUNGSNUMMER")
    a.eu_dok_nr = doc.findtext("EU_DOK_NR")
    a.abstrakt = doc.findtext("ABSTRAKT")
    a.sachgebiet = doc.findtext("SACHGEBIET")
    a.zustimmungsbeduerftig = doc.findtext("ZUSTIMMUNGSBEDUERFTIGKEIT")
    a.source_url = url
    a.schlagworte = []
    for sw in doc.findall("SCHLAGWORT"):
        schlagwort = Schlagwort()
        schlagwort.name = sw.text
        db.session.add(schlagwort)
        a.schlagworte.append(schlagwort)
    log.info("Ablauf %s: %s" % (a.key, a.titel))
    a.titel = a.titel.strip().lstrip('.').strip()
    a = expand_dok_nr(a)
    a.abgeschlossen = DIP_ABLAUF_STATES_FINISHED.get(a.stand, False)
    if 'Originaltext der Frage(n):' in a.abstrakt:
        _, a.abstrakt = a.abstrakt.split('Originaltext der Frage(n):', 1)
    
    for elem in doc.findall("WICHTIGE_DRUCKSACHE"):
        link = elem.findtext("DRS_LINK")
        if link is not None and '#' in link:
            link, hash = link.rsplit('#', 1)
        dokument = dokument_by_id(elem.findtext("DRS_HERAUSGEBER"), 
                'drs', elem.findtext("DRS_NUMMER"), link=link)
        referenz = Referenz()
        referenz.text = elem.findtext("DRS_TYP")
        referenz.dokument = dokument
        db.session.add(referenz)
        a.referenzen.append(referenz)

    for elem in doc.findall("PLENUM"):
        link = elem.findtext("PLPR_LINK")
        if link is not None and '#' in link:
            link, hash = link.rsplit('#', 1)
        dokument = dokument_by_id(elem.findtext("PLPR_HERAUSGEBER"), 
                'plpr', elem.findtext("PLPR_NUMMER"), link=link)
        referenz = Referenz()
        referenz.text = elem.findtext("PLPR_KLARTEXT")
        referenz.seiten = elem.findtext("PLPR_SEITEN")
        referenz.dokument = dokument
        db.session.add(referenz)
        a.referenzen.append(referenz)
    
    db.session.flush()
    scrape_activities(a)
    db.session.commit()


def load_dip():
    for offset in count():
        urlfp = get_dip_with_cookie(BASE_URL % (offset*100))
        root = etree.parse(urlfp, etree.HTMLParser())
        urlfp.close()
        table = root.find(".//table[@summary='Ergebnisliste']")
        if table is None: return
        for result in table.findall(".//a[@class='linkIntern']"):
            url = urljoin(BASE_URL, result.get('href'))
            scrape_ablauf(url)


if __name__ == '__main__':
    load_dip()

