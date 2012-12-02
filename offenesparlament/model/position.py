from datetime import datetime

from offenesparlament.core import db
from offenesparlament.model.util import ModelCore


class Position(db.Model, ModelCore):
    __tablename__ = 'position'

    key = db.Column(db.Unicode())
    zuordnung = db.Column(db.Unicode())
    urheber = db.Column(db.Unicode())
    fundstelle = db.Column(db.Unicode())
    fundstelle_url = db.Column(db.Unicode())
    date = db.Column(db.DateTime())
    quelle = db.Column(db.Unicode())
    typ = db.Column(db.Unicode())

    ablauf_id = db.Column(db.Integer, db.ForeignKey('ablauf.id'))
    dokument_id = db.Column(db.Integer, db.ForeignKey('dokument.id'))
    debatte_id = db.Column(db.Integer, db.ForeignKey('debatte.id'),
            nullable=True)

    zuweisungen = db.relationship('Zuweisung', backref='position', 
            lazy='dynamic')

    beschluesse = db.relationship('Beschluss', backref='position', 
            lazy='dynamic')

    beitraege = db.relationship('Beitrag', lazy='dynamic',
            backref='position')

    def to_ref(self):
        return {
                'id': self.id,
                'key': self.key,
                'urheber': self.urheber,
                'fundstelle': self.fundstelle,
                'wahlperiode': self.ablauf.wahlperiode,
                'ablauf': self.ablauf.key
                }

    def to_dict(self):
        data = self.to_ref()
        del data['wahlperiode']
        data.update({
            'zuordnung': self.zuordnung,
            'fundstelle_url': self.fundstelle_url,
            'date': self.date,
            'quelle': self.quelle,
            'typ': self.typ,
            'ablauf': self.ablauf.to_ref(),
            'debatte': self.debatte.to_ref() if self.debatte else None,
            'dokument': self.dokument.to_ref() if self.dokument else None,
            'zuweisungen': [z.to_ref() for z in self.zuweisungen],
            'beschluesse': [b.to_ref() for b in self.beschluesse],
            'beitraege': [b.to_dict() for b in self.beitraege],
            'created_at': self.created_at,
            'updated_at': self.updated_at
            })
        return data

