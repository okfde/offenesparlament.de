import logging
from lxml import etree

from offenesparlament.scrape.xml import news
from offenesparlament.core import db
from offenesparlament.model import Gremium

log = logging.getLogger(__name__)

AUSSCHUSS_INDEX_URL = "http://www.bundestag.de/xml/ausschuesse/index.xml"

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


def load_index():
    doc = etree.parse(AUSSCHUSS_INDEX_URL)
    for info_url in doc.findall("//ausschussDetailXML"):
        load_ausschuss(info_url.text)

def load_ausschuss(url):
    doc = etree.parse(url)
    a = Gremium.query.filter_by(source_url=url).first()
    if a is None:
        a = Gremium()
    a.key = doc.findtext('/ausschussId')
    a.name = doc.findtext('/ausschussName')
    log.info("Ausschuss (%s): %s" % (a.key, a.name))
    a.aufgabe = doc.findtext('/ausschussAufgabe')
    a.image_url = doc.findtext('/ausschussBildURL')
    a.image_copyright = doc.findtext('/ausschussCopyright')
    a.rss_url = RSS_FEEDS.get(a.key)
    a.type = 'ausschuss'
    db.session.add(a)
    db.session.commit()
    for url in doc.findall("//news/detailsXML"):
        news.load_item(url.text, gremium=a)


if __name__ == '__main__':
    load_index()

