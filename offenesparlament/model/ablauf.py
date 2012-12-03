from datetime import datetime

from offenesparlament.core import db
from offenesparlament.model.schlagwort import schlagworte
from offenesparlament.model.util import ModelCore

class Ablauf(db.Model, ModelCore):
    __tablename__ = 'ablauf'

    key = db.Column(db.Unicode())
    source_url = db.Column(db.Unicode())
    wahlperiode = db.Column(db.Unicode())
    typ = db.Column(db.Unicode())
    klasse = db.Column(db.Unicode())
    titel = db.Column(db.Unicode())
    initiative = db.Column(db.Unicode())
    stand = db.Column(db.Unicode())
    signatur = db.Column(db.Unicode())
    gesta_id = db.Column(db.Unicode())
    eu_dok_nr = db.Column(db.Unicode())
    eur_lex_url = db.Column(db.Unicode())
    eur_lex_pdf = db.Column(db.Unicode())
    consilium_url = db.Column(db.Unicode())
    abstrakt = db.Column(db.Unicode())
    zustimmungsbeduerftig = db.Column(db.Unicode())
    sachgebiet = db.Column(db.Unicode())
    abgeschlossen = db.Column(db.Boolean())

    schlagworte = db.relationship('Schlagwort',
        secondary=schlagworte,
        backref=db.backref('ablaeufe', lazy='dynamic'))

    positionen = db.relationship('Position', backref='ablauf',
                           lazy='dynamic', order_by='Position.date.desc()')

    @property
    def latest(self):
        dates = [p.date for p in self.positionen if p.date]
        if not len(dates):
            return datetime.utcnow()
        return max(dates)

    def to_ref(self):
        return {
                'id': self.id,
                'source_url': self.source_url,
                'key': self.key,
                'wahlperiode': self.wahlperiode,
                'titel': self.titel
                }

    def to_dict(self):
        data = self.to_ref()
        data.update({
            'typ': self.typ,
            'klasse': self.klasse,
            'initiative': self.initiative,
            'stand': self.stand,
            'signatur': self.signatur,
            'gesta_id': self.gesta_id,
            'eu_dok_nr': self.eu_dok_nr,
            'eur_lex_pdf': self.eur_lex_pdf,
            'eur_lex_url': self.eur_lex_url,
            'consilium_url': self.consilium_url,
            'abstrakt': self.abstrakt,
            'zustimmungsbeduerftig': self.zustimmungsbeduerftig,
            'sachgebiet': self.sachgebiet,
            'schlagworte': [s.name for s in self.schlagworte],
            'positionen': [p.to_ref() for p in self.positionen],
            'referenzen': [r.to_ref() for r in self.referenzen],
            'created_at': self.created_at,
            'updated_at': self.updated_at
            })
        return data

    def to_index(self):
        data = super(Ablauf, self).to_index()
        data['positionen'] = [p.to_dict() for p in \
                self.positionen]
        data['positionen'] = [p.to_dict() for p in self.positionen]
        dates = [p['date'] for p in data['positionen'] if p['date'] is not None]
        if len(dates):
            data['date'] = max(dates)
        return data
