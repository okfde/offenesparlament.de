from datetime import datetime

from offenesparlament.core import db


class Sitzung(db.Model):
    __tablename__ = 'sitzung'

    id = db.Column(db.Integer, primary_key=True)
    wahlperiode = db.Column(db.Integer())
    nummer = db.Column(db.Integer())
    titel = db.Column(db.Unicode())
    date = db.Column(db.DateTime())
    source_url = db.Column(db.Unicode())

    debatten = db.relationship('Debatte', backref='sitzung',
                           lazy='dynamic', order_by='Debatte.nummer.asc()')

    zitate = db.relationship('Zitat', backref='sitzung',
                           lazy='dynamic', order_by='Zitat.sequenz.asc()')

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow)

    def to_ref(self):
        return {
            'id': self.id,
            'wahlperiode': self.wahlperiode,
            'nummer': self.nummer,
            'date': self.date,
            'titel': self.titel
            }

    def to_dict(self):
        data = self.to_ref()
        data.update({
            'debatten': [d.to_ref() for d in self.debatten],
            'created_at': self.created_at,
            'updated_at': self.updated_at
            })
        return data

