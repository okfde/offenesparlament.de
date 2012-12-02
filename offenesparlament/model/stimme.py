from offenesparlament.core import db
from offenesparlament.model.util import ModelCore


class Stimme(db.Model, ModelCore):
    __tablename__ = 'stimme'

    entscheidung = db.Column(db.Unicode())

    person_id = db.Column(db.Integer, db.ForeignKey('person.id'), 
            nullable=True)
    abstimmung_id = db.Column(db.Integer, db.ForeignKey('abstimmung.id'), 
            nullable=True)

    def to_ref(self):
        return {
            'id': self.id,
            'abstimmung': self.abstimmung.thema,
            'person': self.person.to_ref(),
            }

    def to_dict(self):
        data = self.to_ref()
        data.update({
            'abstimmung': self.abstimmung.to_ref(),
            'person': self.person.to_ref(),
            'created_at': self.created_at,
            'updated_at': self.updated_at
            })
        return data

