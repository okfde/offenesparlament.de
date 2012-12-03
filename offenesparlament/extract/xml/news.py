import logging
from lxml import etree
from datetime import datetime

import sqlaload as sl

from offenesparlament.extract.util import _xml
from offenesparlament.core import etl_engine

AKTUELL_URL = "https://www.bundestag.de/xml/aktuell/index.xml"

log = logging.getLogger(__name__)

def strpa(d):
    try:
        return datetime.strptime(d, "%d.%m.%Y").isoformat()
    except ValueError:
        return datetime.strptime(d, "%d.%m.%y").isoformat()


def load_item(url, engine, gremium=None):
    table = sl.get_table(engine, 'news')
    item = sl.find_one(engine, table, source_url=url)
    if item is not None:
        if gremium is not None:
            item['gremium'] = gremium['key']
            sl.upsert(engine, table, item, unique=['source_url'])
        return
    try:
        doc = _xml(url)
    except Exception, e:
        log.exception(e)
        return
    item = {}
    log.info('News item: %s' % doc.findtext('/title'))
    item['source_url'] = url
    item['title'] = doc.findtext('/title')
    item['text'] = doc.findtext('/text')
    if doc.findtext('/date'):
        item['date'] = strpa(doc.findtext('/date'))
    item['image_url'] = doc.findtext('/imageURL')
    item['image_copyright'] = doc.findtext('/imageCopyright')
    if doc.findtext('/imageLastChanged'):
        item['image_changed_at'] = strpa(
                doc.findtext('/imageLastChanged'))

    if gremium:
        item['gremium'] = gremium['key']
    sl.upsert(engine, table, item, unique=['source_url'])
    prev = doc.findtext('/dokumentInfo/previous')
    if prev is not None and len(prev):
        load_item(prev, engine)

def load_index(engine):
    doc = _xml(AKTUELL_URL)
    for info_url in doc.findall("//detailsXML"):
        if not info_url.text or 'impressum' in info_url.text:
            continue
        load_item(info_url.text, engine)


if __name__ == '__main__':
    engine = etl_engine()
    print "DESTINATION", engine
    load_index(engine)

