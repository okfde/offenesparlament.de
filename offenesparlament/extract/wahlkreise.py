#coding: utf-8
import logging
import urllib 
from urlparse import urljoin
from lxml import html

import sqlaload as sl
from offenesparlament.core import etl_engine

RESOLVER = "http://www.bundestag.de/cgibin/wkreis2009neu.pl"

log = logging.getLogger(__name__)

def load_wahlkreise(engine):
    Plz = sl.get_table(engine, 'plz')
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
        plz = {'plz': plz}
        plz['wk_url'] = wk_e.find("a").get('href')
        plz['wk_name'] = wk_e.find(".//strong").text
        plz['wk_id'] = plz['wk_url'].rsplit("=",1)[-1]
        plz['wk_url'] = urljoin(RESOLVER, plz['wk_url'])
        log.info("PLZ: %s, Wahlkreis: %s" % (plz['plz'], plz['wk_name']))
        sl.upsert(engine, Plz, plz, unique=['plz'])

if __name__ == '__main__':
    engine = etl_engine()
    print "DESTINATION", engine
    load_wahlkreise(engine)
