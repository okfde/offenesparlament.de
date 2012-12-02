from datetime import datetime

from offenesparlament.core import db


beschluesse_dokumente = db.Table('beschluesse_dokumente',
    db.Column('dokument_id', db.Integer, db.ForeignKey('beschluss.id')),
    db.Column('beschluss_id', db.Integer, db.ForeignKey('dokument.id'))
)


class Dokument(db.Model):
    __tablename__ = 'dokument'
    
    id = db.Column(db.Integer, primary_key=True)
    nummer = db.Column(db.Unicode())
    hrsg = db.Column(db.Unicode())
    typ = db.Column(db.Unicode())
    link = db.Column(db.Unicode())
    
    referenzen = db.relationship('Referenz', backref='dokument',
                           lazy='dynamic')
    
    positionen = db.relationship('Position', backref='dokument',
                           lazy='dynamic')

    beschluesse = db.relationship('Beschluss', secondary=beschluesse_dokumente,
        backref=db.backref('dokumente', lazy='dynamic'))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow)
    
    @property
    def typ_lang(self):
        return {'plpr': 'Plenarprotokoll',
                'drs': 'Drucksache'}.get(self.typ.lower(), 
                        'Drucksache')
    
    @property
    def name(self):
        return "%s (%s) %s" % (self.typ_lang, self.hrsg, self.nummer)

    def to_ref(self):
        return {
                'id': self.id,
                'name': self.name,
                'nummer': self.nummer,
                'hrsg': self.hrsg,
                'typ': self.typ,
                'link': self.link
                }

    def to_dict(self):
        data = self.to_ref()
        data.update({
            'referenzen': [r.to_ref() for r in self.referenzen],
            'positionen': [p.to_ref() for p in self.positionen],
            'beschluesse': [b.to_ref() for b in self.beschluesse],
            'created_at': self.created_at,
            'updated_at': self.updated_at
            })
        return data

