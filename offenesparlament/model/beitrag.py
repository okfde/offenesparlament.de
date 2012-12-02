from datetime import datetime

from offenesparlament.core import db
from offenesparlament.model.util import ModelCore


class Beitrag(db.Model, ModelCore):
    __tablename__ = 'beitrag'

    seite = db.Column(db.Unicode())
    art = db.Column(db.Unicode())

    person_id = db.Column(db.Integer, db.ForeignKey('person.id'))
    rolle_id = db.Column(db.Integer, db.ForeignKey('rolle.id'))
    position_id = db.Column(db.Integer, db.ForeignKey('position.id'))

    def to_ref(self):
        return {
                'id': self.id,
                'seite': self.seite,
                'art': self.art,
                'position': self.position.id,
                'rolle': self.rolle.id if self.rolle else None,
                'person': self.person.id if self.person else None
                }

    def to_dict(self):
        data = self.to_ref()
        data.update({
            'person': self.person.to_ref() if self.person else None,
            'rolle': self.rolle.to_ref() if self.rolle else None,
            'position': self.position.to_ref(),
            'created_at': self.created_at,
            'updated_at': self.updated_at
            })
        return data


