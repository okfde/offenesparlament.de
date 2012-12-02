#coding: utf-8
from datetime import datetime

from offenesparlament.core import db


class Abstimmung(db.Model):
    __tablename__ = 'abstimmung'

    id = db.Column(db.Integer, primary_key=True)
    thema = db.Column(db.Unicode())
    datum = db.Column(db.DateTime, default=datetime.utcnow)

    stimmen = db.relationship('Stimme', backref='abstimmung',
                              lazy='dynamic')

    @property
    def titel(self):
        titel = self.thema
        s1 = titel.split(u'über', 1)
        s2 = titel.split(u'Über', 1)
        if len(s1) > 1:
            titel = s1[-1]
        elif len(s2) > 1:
            titel = s2[-1]

        titel = titel.split('Drs', 1)[0]
        titel = titel.rstrip(';- .')

        t = titel.split()
        t[0] = t[0].capitalize()
        titel = ' '.join(t)
        return titel

    def to_ref(self):
        return {
            'id': self.id,
            'thema': self.thema,
            }

    def to_dict(self):
        data = self.to_ref()
        data.update({
            'stimmen': [s.to_ref() for s in self.stimmen],
            'created_at': self.created_at,
            'updated_at': self.updated_at
            })
        return data

