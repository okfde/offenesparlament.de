from datetime import datetime

from offenesparlament.core import db
from offenesparlament.model.util import ModelCore


class NewsItem(db.Model, ModelCore):
    __tablename__ = 'news_item'

    source_url = db.Column(db.Unicode)
    title = db.Column(db.Unicode)
    text = db.Column(db.UnicodeText)
    date = db.Column(db.DateTime)
    image_url = db.Column(db.Unicode)
    image_copyright = db.Column(db.Unicode)
    image_changed_at = db.Column(db.DateTime)

    gremium_id = db.Column(db.Integer, db.ForeignKey('gremium.id'))

    def to_dict(self):
        return {
            'id': self.id,
            'source_url': self.source_url,
            'title': self.title,
            'text': self.text,
            'date': self.date,
            'image_url': self.image_url,
            'image_copyright': self.image_copyright,
            'image_changed_at': self.image_changed_at,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'gremium': self.gremium.to_ref()
            }

    def to_ref(self):
        return {
            'id': self.id,
            'source_url': self.source_url,
            'title': self.title,
            'gremium_id': self.gremium.id
            }
