from datetime import datetime

from offenesparlament.core import db


class Postleitzahl(db.Model):
    __tablename__ = 'postleitzahl'

    plz = db.Column(db.Unicode, primary_key=True)
    wahlkreis_id = db.Column(db.Integer, db.ForeignKey('wahlkreis.id'))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow)


class Wahlkreis(db.Model):
    __tablename__ = 'wahlkreis'

    id = db.Column(db.Integer, primary_key=True)
    nummer = db.Column(db.Unicode)
    name = db.Column(db.Unicode)
    url = db.Column(db.Unicode)

    mdbs = db.relationship('Rolle', backref='wahlkreis',
                           lazy='dynamic')
    plzs = db.relationship('Postleitzahl', backref='wahlkreis',
                           lazy='dynamic')

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow)

    def to_ref(self):
        return {
                'id': self.id,
                'nummer': self.nummer,
                'name': self.name,
                'url': self.url,
            }

    def to_dict(self):
        data = self.to_ref()
        data.update({
            'mdbs': [m.to_ref() for m in self.mdbs],
            'plzs': [p.plz for p in self.plzs],
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            })
        return data

