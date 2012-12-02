from datetime import datetime

from offenesparlament.core import db
from offenesparlament.model.util import ModelCore


class Debatte(db.Model, ModelCore):
    __tablename__ = 'debatte'

    tops = db.Column(db.Unicode())
    nummer = db.Column(db.Integer())
    titel = db.Column(db.Unicode())
    text = db.Column(db.Unicode())

    sitzung_id = db.Column(db.Integer, db.ForeignKey('sitzung.id'))

    zitate = db.relationship('Zitat', backref='debatte',
                           lazy='dynamic', order_by='Zitat.sequenz.asc()')

    positionen = db.relationship('Position', backref='debatte',
                           lazy='dynamic')

    def to_ref(self):
        return {
            'id': self.id,
            'nummer': self.nummer,
            'titel': self.titel
            }

    def to_dict(self):
        data = self.to_ref()
        data.update({
            'sitzung': self.sitzung.to_ref() if self.sitzung else None,
            'text': self.text,
            'positionen': [p.to_ref() for p in self.positionen],
            'created_at': self.created_at,
            'updated_at': self.updated_at
            })
        return data

