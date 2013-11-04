import logging

import sqlaload as sl

from offenesparlament.data.lib.constants import GREMIUM_RSS_FEEDS
from offenesparlament.data.lib.retrieval import _xml
from offenesparlament.data.lib.refresh import check_tags

log = logging.getLogger(__name__)

AUSSCHUSS_INDEX_URL = "http://www.bundestag.de/xml/ausschuesse/index.xml"
URL_PATTERN = "http://www.bundestag.de/bundestag/ausschuesse17/%s/index.jsp"


def scrape_index():
    response, doc = _xml(AUSSCHUSS_INDEX_URL)
    for info_url in doc.findall("//ausschussDetailXML"):
        yield info_url.text.strip()


def scrape_gremium(engine, url, force=False):
    table = sl.get_table(engine, 'gremium')
    response, doc = _xml(url)
    a = sl.find_one(engine, table, source_url=url)
    if a is None:
        a = {'source_url': url}
    a = check_tags(a, response, force)
    a['key'] = doc.findtext('/ausschussId')
    a['name'] = doc.findtext('/ausschussName')
    log.info("Ausschuss (%s): %s" % (a['key'], a['name']))
    a['aufgabe'] = doc.findtext('/ausschussAufgabe')
    a['image_url'] = doc.findtext('/ausschussBildURL')
    a['image_copyright'] = doc.findtext('/ausschussCopyright')
    a['rss_url'] = GREMIUM_RSS_FEEDS.get(a['key'])
    a['url'] = URL_PATTERN % a['key']
    a['type'] = 'ausschuss'
    sl.upsert(engine, table, a, unique=['key'])
    return a

