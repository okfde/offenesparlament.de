import logging
import sqlaload as sl

from offenesparlament.core import etl_engine

from offenesparlament.core import db
from offenesparlament.model import Gremium

log = logging.getLogger(__name__)


def load_gremium(engine, data):
    gremium = Gremium.query.filter_by(key=data.get('key')).first()
    if gremium is None:
        gremium = Gremium()

    gremium.key = data.get('key')
    gremium.source_url = data.get('source_url')
    gremium.name = data.get('name')
    gremium.typ = data.get('type')
    gremium.url = data.get('url')
    gremium.aufgabe = data.get('aufgabe')
    gremium.rss_url = data.get('rss_url')
    gremium.image_url = data.get('image_url')
    gremium.image_copyright = data.get('image_copyright')
    db.session.add(gremium)
    db.session.commit()
    return gremium




