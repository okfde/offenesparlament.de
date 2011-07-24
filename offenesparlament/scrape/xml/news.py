import logging
from lxml import etree
from datetime import datetime

from offenesparlament.core import db
from offenesparlament.model import NewsItem

AKTUELL_URL = "http://www.bundestag.de/xml/aktuell/index.xml"

log = logging.getLogger(__name__)

def load_item(url, gremium=None):
    item = NewsItem.query.filter_by(source_url=url).first()
    if item is not None:
        if gremium is not None:
            item.gremium = gremium
            db.session.add(gremium)
        return
    doc = etree.parse(url)
    item = NewsItem()
    log.info('News item: %s' % doc.findtext('/title'))
    item.source_url = url
    item.title = doc.findtext('/title')
    item.text = doc.findtext('/text')
    item.date = datetime.strptime(doc.findtext('/date'), 
                                  '%d.%m.%Y')
    item.image_url = doc.findtext('/imageURL')
    item.image_copyright = doc.findtext('/imageCopyright')
    if doc.findtext('/imageLastChanged'):
        item.image_changed_at = datetime.strptime(
                doc.findtext('/imageLastChanged'), 
                '%d.%m.%Y')

    if gremium:
        item.gremium = gremium
    db.session.add(item)
    db.session.commit()
    prev = doc.findtext('/dokumentInfo/previous')
    if prev is not None and len(prev):
        load_item(prev)

def load_index():
    doc = etree.parse(AKTUELL_URL)
    for info_url in doc.findall("//detailsXML"):
        if not info_url.text or 'impressum' in info_url.text:
            continue
        load_item(info_url.text)
        db.session.commit()




if __name__ == '__main__':
    load_index()

