import logging

import sqlaload as sl

from offenesparlament.data.lib.constants import GREMIUM_RSS_FEEDS
from offenesparlament.data.lib.retrieval import _xml
from offenesparlament.core import etl_engine

log = logging.getLogger(__name__)

AUSSCHUSS_INDEX_URL = "http://www.bundestag.de/xml/ausschuesse/index.xml"
URL_PATTERN = "http://www.bundestag.de/bundestag/ausschuesse17/%s/index.jsp"

def load_index(engine):
    doc = _xml(AUSSCHUSS_INDEX_URL)
    table = sl.get_table(engine, 'gremium')
    for info_url in doc.findall("//ausschussDetailXML"):
        load_ausschuss(info_url.text, engine, table)

def load_ausschuss(url, engine, table):
    doc = _xml(url)
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
    sl.upsert(engine, table, a, unique=['key'])


if __name__ == '__main__':
    engine = etl_engine()
    print "DESTINATION", engine
    load_index(engine)

