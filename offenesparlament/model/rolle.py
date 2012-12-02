from offenesparlament.core import db
from offenesparlament.model.util import ModelCore

class Rolle(db.Model, ModelCore):
    __tablename__ = 'rolle'

    person_id = db.Column(db.Integer, db.ForeignKey('person.id'))
    mdb_id = db.Column(db.Unicode)
    status = db.Column(db.Unicode)
    funktion = db.Column(db.Unicode)
    fraktion = db.Column(db.Unicode)
    gewaehlt = db.Column(db.Unicode)
    ressort = db.Column(db.Unicode)
    land = db.Column(db.Unicode)
    austritt = db.Column(db.DateTime)

    wahlkreis_id = db.Column(db.Integer, db.ForeignKey('wahlkreis.id'))

    beitraege = db.relationship('Beitrag', backref='rolle',
            lazy='dynamic')

    def to_ref(self):
        return {
            'id': self.id,
            'mdb_id': self.mdb_id,
            'status': self.status,
            'funktion': self.funktion,
            'fraktion': self.fraktion,
            'ressort': self.ressort,
            'land': self.land,
            'wahlkreis': self.wahlkreis.to_ref() if self.wahlkreis else None,
            }

    def to_dict(self):
        data = self.to_ref()
        data.update({
            'person': self.person.to_ref(),
            'gewaehlt': self.gewaehlt,
            'austritt': self.austritt,
            'created_at': self.created_at,
            'updated_at': self.updated_at
            })
        return data

