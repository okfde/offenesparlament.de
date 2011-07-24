#coding: utf-8
import logging
import urllib 
from lxml import html

from offenesparlament.core import db
from offenesparlament.model import Wahlkreis, Postleitzahl

RESOLVER = "http://www.bundestag.de/cgibin/wkreis2009neu.pl"

log = logging.getLogger(__name__)

def load_wahlkreise():
    for i in xrange(10000, 100000):
        q = urllib.urlencode([("PLZ", str(i)), ("ORT", "")])
        urlfh = urllib.urlopen(RESOLVER, q)
        doc = html.parse(urlfh)
        urlfh.close()
        result = doc.find('//tr[@class="alternativ"]')
        if result is None:
            log.debug("No PLZ: %s" % i)
            continue
        plz_e, ort_e, wk_e = result.findall("td")
        plz = plz_e.xpath("string()").strip()
        #ort = ort_e.xpath("string()").strip()
        wk_url = wk_e.find("a").get('href')
        wk_name = wk_e.find(".//strong").text
        wk_id = wk_url.rsplit("=",1)[-1]
        wk = Wahlkreis.query.filter_by(nummer=wk_id).first()
        if wk is None:
            wk = Wahlkreis()
        wk.nummer = wk_id
        wk.name = wk_name
        wk.url = wk_url
        o = Postleitzahl.query.filter_by(plz=plz).first()
        if o is None:
            o = Postleitzahl()
        o.plz = plz
        o.wahlkreis = wk
        log.info("PLZ: %s, Wahlkreis: %s" % (plz, wk_name))
        db.session.add(wk)
        db.session.add(o)
        db.session.commit()

if __name__ == '__main__':
    load_wahlkreise()
