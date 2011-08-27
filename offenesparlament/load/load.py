import sys
import logging

from webstore.client import URL as WebStore

from offenesparlament.core import db
from offenesparlament.model import Gremium

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.NOTSET)


def load_gremien(ws):
    GremiumSource = ws['gremium']
    for data in GremiumSource:
        gremium = db.session.query(Gremium).filter_by(key=data.get('key')).first()
        if gremium is None:
            gremium = Gremium()
        gremium.name = data.get('name')
        gremium.key = data.get('key')
        gremium.type = data.get('type')
        gremium.url = data.get('url')
        gremium.aufgabe = data.get('aufgabe')
        gremium.rss_url = data.get('rss_url')
        gremium.image_url = data.get('image_url')
        gremium.image_copyright = data.get('image_copyright')
        db.session.add(gremium)
    db.session.commit()

def load(ws):
    load_gremien(ws)

if __name__ == '__main__':
    assert len(sys.argv)==2, "Need argument: webstore-url!"
    ws, _ = WebStore(sys.argv[1])
    print "SOURCE", ws
    load(ws)


