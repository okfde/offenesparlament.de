from datetime import datetime

from offenesparlament.core import db


referenzen = db.Table('referenzen',
    db.Column('referenz_id', db.Integer, db.ForeignKey('referenz.id')),
    db.Column('ablauf_id', db.Integer, db.ForeignKey('ablauf.id'))
)


class Referenz(db.Model):
    __tablename__ = 'referenz'

    id = db.Column(db.Integer, primary_key=True)
    seiten = db.Column(db.Unicode())
    text = db.Column(db.Unicode())
    dokument_id = db.Column(db.Integer, db.ForeignKey('dokument.id'))

    ablaeufe = db.relationship('Ablauf', secondary=referenzen,
        backref=db.backref('referenzen', lazy='dynamic'))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow)

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

