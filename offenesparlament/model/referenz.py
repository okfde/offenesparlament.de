from offenesparlament.core import db
from offenesparlament.model.util import ModelCore


referenzen = db.Table('referenzen',
    db.Column('referenz_id', db.Integer, db.ForeignKey('referenz.id')),
    db.Column('ablauf_id', db.Integer, db.ForeignKey('ablauf.id'))
)


class Referenz(db.Model, ModelCore):
    __tablename__ = 'referenz'

    seiten = db.Column(db.Unicode())
    text = db.Column(db.Unicode())
    dokument_id = db.Column(db.Integer, db.ForeignKey('dokument.id'))

    ablaeufe = db.relationship('Ablauf', secondary=referenzen,
        backref=db.backref('referenzen', lazy='dynamic'))

    def to_ref(self):
        return {
                'id': self.id,
                'seiten': self.seiten,
                'text': self.text,
                'dokument': self.dokument.id
                }

    def to_dict(self):
        data = self.to_ref()
        data.update({
            'dokument': self.dokument.to_ref(),
            'ablaeufe': [a.to_ref() for a in self.ablaeufe],
            'created_at': self.created_at,
            'updated_at': self.updated_at
            })
        return data

