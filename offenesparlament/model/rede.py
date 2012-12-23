from datetime import datetime

from offenesparlament.core import db
from offenesparlament.model.util import ModelCore


class Rede(db.Model, ModelCore):
    __tablename__ = 'rede'

    webtv_id = db.Column(db.Integer())
    sitzung_id = db.Column(db.Integer, db.ForeignKey('sitzung.id'))
    debatte_id = db.Column(db.Integer, db.ForeignKey('debatte.id'))
    redner_id = db.Column(db.Integer, db.ForeignKey('person.id'))

    zitate = db.relationship('Zitat', backref='rede',
                             lazy='dynamic', order_by='Zitat.sequenz.asc()')

    def to_ref(self):
        return {
            'id': self.id,
            'webtv_id': self.webtv_id,
            'redner': self.redner.fingerprint if self.redner else None,
            }

    def to_dict(self):
        data = self.to_ref()
        data.update({
            'sitzung': self.sitzung.to_ref() if self.sitzung else None,
            'debatte': self.debatte.to_ref() if self.debatte else None,
            'created_at': self.created_at,
            'updated_at': self.updated_at
            })
        return data

    def to_index(self):
        data = super(Rede, self).to_index()
        data['sitzung'] = self.sitzung.to_dict()
        data['debatte'] = self.debatte.to_dict()
        data['zitate'] = [z.to_dict() for z in self.zitate]
        return data

