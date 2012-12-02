from offenesparlament.core import db
from offenesparlament.model.util import ModelCore


class Zitat(db.Model, ModelCore):
    __tablename__ = 'zitat'

    sequenz = db.Column(db.Integer())
    sprecher = db.Column(db.Unicode())
    redner = db.Column(db.Unicode())
    text = db.Column(db.Unicode())
    typ = db.Column(db.Unicode())
    speech_id = db.Column(db.Integer())
    source_url = db.Column(db.Unicode())

    person_id = db.Column(db.Integer, db.ForeignKey('person.id'),
            nullable=True)
    sitzung_id = db.Column(db.Integer, db.ForeignKey('sitzung.id'))
    debatte_id = db.Column(db.Integer, db.ForeignKey('debatte.id'))

    def to_ref(self):
        return {
            'id': self.id,
            'sequenz': self.sequenz,
            'speech_id': self.speech_id,
            'sprecher': self.sprecher,
            'typ': self.typ,
            }

    def to_dict(self):
        data = self.to_ref()
        data.update({
            'text': self.text,
            'source_url': self.source_url,
            'sitzung': self.sitzung.to_ref() if self.sitzung else None,
            'person': self.person.to_ref() if self.person else None,
            'debatte': self.debatte.to_ref() if self.debatte else None,
            'created_at': self.created_at,
            'updated_at': self.updated_at
            })
        return data

