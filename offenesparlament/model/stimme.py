from datetime import datetime

from offenesparlament.core import db


class Stimme(db.Model):
    __tablename__ = 'stimme'

    id = db.Column(db.Integer, primary_key=True)
    entscheidung = db.Column(db.Unicode())

    person_id = db.Column(db.Integer, db.ForeignKey('person.id'), 
            nullable=True)
    abstimmung_id = db.Column(db.Integer, db.ForeignKey('abstimmung.id'), 
            nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow)

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

