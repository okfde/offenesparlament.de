#coding: utf-8
import logging
import urllib 
from urlparse import urljoin
import sys
from lxml import html

from webstore.client import URL as WebStore

RESOLVER = "http://www.bundestag.de/cgibin/wkreis2009neu.pl"

log = logging.getLogger(__name__)

def load_wahlkreise(db):
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
        db['plz'].writerow(plz, unique_columns=['plz'])

if __name__ == '__main__':
    assert len(sys.argv)==2, "Need argument: webstore-url!"
    db, _ = WebStore(sys.argv[1])
    print "DESTINATION", db
    load_wahlkreise(db)
