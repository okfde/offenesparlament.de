import logging
import sys
from lxml import etree
from datetime import datetime

from webstore.client import URL as WebStore

AKTUELL_URL = "http://www.bundestag.de/xml/aktuell/index.xml"

log = logging.getLogger(__name__)

def load_item(url, db, gremium=None):
    table = db['news']
    item = table.find_one(source_url=url)
    if item is not None:
        if gremium is not None:
            item['gremium'] = gremium['key']
            table.writerow(item, unique_columns=['source_url'])
        return
    try:
        doc = etree.parse(url)
    except Exception, e:
        log.exception(e)
        return
    item = {}
    log.info('News item: %s' % doc.findtext('/title'))
    item['source_url'] = url
    item['title'] = doc.findtext('/title')
    item['text'] = doc.findtext('/text')
    item['date'] = datetime.strptime(doc.findtext('/date'), 
                                  '%d.%m.%Y').isoformat()
    item['image_url'] = doc.findtext('/imageURL')
    item['image_copyright'] = doc.findtext('/imageCopyright')
    if doc.findtext('/imageLastChanged'):
        item['image_changed_at'] = datetime.strptime(
                doc.findtext('/imageLastChanged'), 
                '%d.%m.%Y').isoformat()

    if gremium:
        item['gremium'] = gremium['key']
    table.writerow(item, unique_columns=['source_url'])
    prev = doc.findtext('/dokumentInfo/previous')
    if prev is not None and len(prev):
        load_item(prev, db)

def load_index(db):
    doc = etree.parse(AKTUELL_URL)
    for info_url in doc.findall("//detailsXML"):
        if not info_url.text or 'impressum' in info_url.text:
            continue
        load_item(info_url.text, db)




if __name__ == '__main__':
    assert len(sys.argv)==2, "Need argument: webstore-url!"
    db, _ = WebStore(sys.argv[1])
    print "DESTINATION", db
    load_index(db)

