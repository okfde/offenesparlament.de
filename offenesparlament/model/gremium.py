from offenesparlament.core import db
from offenesparlament.model.util import ModelCore


class Gremium(db.Model, ModelCore):
    __tablename__ = 'gremium'

    vorsitz_id = db.Column(db.Integer, db.ForeignKey('person.id'))
    stellv_vorsitz_id = db.Column(db.Integer, db.ForeignKey('person.id'))
    source_url = db.Column(db.Unicode)
    rss_url = db.Column(db.Unicode)
    name = db.Column(db.Unicode)
    url = db.Column(db.Unicode)
    key = db.Column(db.Unicode)
    typ = db.Column(db.Unicode)
    aufgabe = db.Column(db.Unicode)
    image_url = db.Column(db.Unicode)
    image_copyright = db.Column(db.Unicode)

    zuweisungen = db.relationship('Zuweisung', backref='gremium', 
            lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'vorsitz': self.vorsitz.to_ref() if \
                    self.vorsitz else None,
            'stellv_vorsitz': self.stellv_vorsitz.to_ref() if \
                    self.stellv_vorsitz else None,
            'source_url': self.source_url,
            'rss_url': self.rss_url,
            'name': self.name,
            'url': self.url,
            'key': self.key,
            'typ': self.typ,
            'aufgabe': self.aufgabe,
            'image_url': self.image_url,
            'image_copyright': self.image_copyright,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'obleute': [m.to_ref() for m in self.obleute],
            'mitglieder': [m.to_ref() for m in self.mitglieder],
            'stellvertreter': [m.to_ref() for m in self.stellvertreter],
            }

    def to_ref(self):
        return {
            'id': self.id,
            'source_url': self.source_url,
            'name': self.name,
            'key': self.key
            }

