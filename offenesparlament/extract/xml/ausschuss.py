import logging
import sys
from lxml import etree

from webstore.client import URL as WebStore

from offenesparlament.extract.xml import news


log = logging.getLogger(__name__)
logging.basicConfig(level=logging.NOTSET)


AUSSCHUSS_INDEX_URL = "http://www.bundestag.de/xml/ausschuesse/index.xml"
URL_PATTERN = "http://www.bundestag.de/bundestag/ausschuesse17/%s/index.jsp"

RSS_FEEDS = {
        "a11": "http://www.bundestag.de/rss_feeds/arbeitsoziales.rss",
        "a03": "http://www.bundestag.de/rss_feeds/auswaertiges.rss",
        "a18": "http://www.bundestag.de/rss_feeds/bildung.rss",
        "a10": "http://www.bundestag.de/rss_feeds/landwirtschaftverbraucher.rss",
        "a21": "http://www.bundestag.de/rss_feeds/eu.rss",
        "a13": "http://www.bundestag.de/rss_feeds/familie.rss",
        "a07": "http://www.bundestag.de/rss_feeds/finanzen.rss",
        "a14": "http://www.bundestag.de/rss_feeds/gesundheit.rss",
        "a08": "http://www.bundestag.de/rss_feeds/haushalt.rss",
        "a04": "http://www.bundestag.de/rss_feeds/inneres.rss",
        "a22": "http://www.bundestag.de/rss_feeds/kultur.rss",
        "a17": "http://www.bundestag.de/rss_feeds/menschenrechte.rss",
        "a02": "http://www.bundestag.de/rss_feeds/petitionen.rss",
        "a06": "http://www.bundestag.de/rss_feeds/recht.rss",
        "a05": "http://www.bundestag.de/rss_feeds/sport.rss",
        "a20": "http://www.bundestag.de/rss_feeds/tourismus.rss",
        "a16": "http://www.bundestag.de/rss_feeds/umwelt.rss",
        "a15": "http://www.bundestag.de/rss_feeds/verkehr.rss",
        "a14": "http://www.bundestag.de/rss_feeds/verteidigung.rss",
        "a09": "http://www.bundestag.de/rss_feeds/wirtschaft.rss",
        "a19": "http://www.bundestag.de/rss_feeds/entwicklung.rss",
        "eig": "http://www.bundestag.de/rss_feeds/internetenquete.rss"
    }


def load_index(db):
    doc = etree.parse(AUSSCHUSS_INDEX_URL)
    for info_url in doc.findall("//ausschussDetailXML"):
        load_ausschuss(info_url.text, db)

def load_ausschuss(url, db):
    doc = etree.parse(url)
    a = {'source_url': url}
    a['key'] = doc.findtext('/ausschussId')
    a['name'] = doc.findtext('/ausschussName')
    log.info("Ausschuss (%s): %s" % (a['key'], a['name']))
    a['aufgabe'] = doc.findtext('/ausschussAufgabe')
    a['image_url'] = doc.findtext('/ausschussBildURL')
    a['image_copyright'] = doc.findtext('/ausschussCopyright')
    a['rss_url'] = RSS_FEEDS.get(a['key'])
    a['url'] = URL_PATTERN % a['key']
    a['type'] = 'ausschuss'
    table = db['gremium']
    table.writerow(a, unique_columns=['key'])
    for url in doc.findall("//news/detailsXML"):
        news.load_item(url.text, db, gremium=a)


if __name__ == '__main__':
    assert len(sys.argv)==2, "Need argument: webstore-url!"
    db, _ = WebStore(sys.argv[1])
    print "DESTINATION", db
    load_index(db)

