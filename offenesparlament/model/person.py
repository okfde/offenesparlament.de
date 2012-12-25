import re
from datetime import datetime

from offenesparlament.core import db
from offenesparlament.model.util import ModelCore


obleute = db.Table('obleute',
    db.Column('gremium_id', db.Integer, db.ForeignKey('gremium.id')),
    db.Column('person_id', db.Integer, db.ForeignKey('person.id'))
)

mitglieder = db.Table('mitglieder',
    db.Column('gremium_id', db.Integer, db.ForeignKey('gremium.id')),
    db.Column('person_id', db.Integer, db.ForeignKey('person.id'))
)

stellvertreter = db.Table('stellvertreter',
    db.Column('gremium_id', db.Integer, db.ForeignKey('gremium.id')),
    db.Column('person_id', db.Integer, db.ForeignKey('person.id'))
)


class Person(db.Model, ModelCore):
    __tablename__ = 'person'

    slug = db.Column(db.Unicode)
    fingerprint = db.Column(db.Unicode)
    source_url = db.Column(db.Unicode)
    mdb_id = db.Column(db.Integer)
    vorname = db.Column(db.Unicode)
    nachname = db.Column(db.Unicode)
    adelstitel = db.Column(db.Unicode)
    titel = db.Column(db.Unicode)
    ort = db.Column(db.Unicode)
    geburtsdatum = db.Column(db.Unicode)
    religion = db.Column(db.Unicode)
    hochschule = db.Column(db.Unicode)
    beruf = db.Column(db.Unicode)
    berufsfeld = db.Column(db.Unicode)
    geschlecht = db.Column(db.Unicode)
    familienstand = db.Column(db.Unicode)
    kinder = db.Column(db.Unicode)
    partei = db.Column(db.Unicode)
    land = db.Column(db.Unicode)
    bio_url = db.Column(db.Unicode)
    bio = db.Column(db.Unicode)
    wissenswertes = db.Column(db.Unicode)
    telefon = db.Column(db.Unicode)
    homepage_url = db.Column(db.Unicode)
    angaben = db.Column(db.Unicode)
    foto_url = db.Column(db.Unicode)
    foto_copyright = db.Column(db.Unicode)
    reden_plenum_url = db.Column(db.Unicode)
    reden_plenum_rss_url = db.Column(db.Unicode)
    twitter_url = db.Column(db.Unicode)
    facebook_url = db.Column(db.Unicode)
    awatch_url = db.Column(db.Unicode)

    rollen = db.relationship('Rolle', backref='person',
                             lazy='dynamic')
    vorsitze = db.relationship('Gremium', backref='vorsitz',
                             primaryjoin='Person.id == Gremium.vorsitz_id',
                             lazy='dynamic')
    stellv_vorsitze = db.relationship('Gremium', backref='stellv_vorsitz',
                             primaryjoin='Person.id == Gremium.stellv_vorsitz_id',
                             lazy='dynamic')

    mitglied = db.relationship('Gremium', secondary=mitglieder,
        backref=db.backref('mitglieder', lazy='dynamic'))

    stellvertreter = db.relationship('Gremium', secondary=stellvertreter,
        backref=db.backref('stellvertreter', lazy='dynamic'))

    obleute = db.relationship('Gremium', secondary=obleute,
        backref=db.backref('obleute', lazy='dynamic'))

    beitraege = db.relationship('Beitrag', backref='person',
                           lazy='dynamic')

    reden = db.relationship('Rede', backref='redner',
                            lazy='dynamic', order_by='Rede.webtv_id.asc()')

    zitate = db.relationship('Zitat', backref='person',
                           lazy='dynamic')

    stimmen = db.relationship('Stimme', backref='person',
                           lazy='dynamic')

    @property
    def name(self):
        name = "%s %s %s" % (self.titel if self.titel else '', \
                self.vorname, self.nachname)
        if self.ort and len(self.ort):
            name += " (%s)" % self.ort
        return name.strip()

    def to_dict(self):
        data = {
                'id': self.id,
                'slug': self.slug,
                'name': self.name,
                'fingerprint': self.fingerprint,
                'source_url': self.source_url,
                'mdb_id': self.mdb_id,
                'vorname': self.vorname,
                'nachname': self.nachname,
                'adelstitel': self.adelstitel,
                'titel': self.titel,
                'ort': self.ort,
                'geburtsdatum': self.geburtsdatum,
                'religion': self.religion,
                'hochschule': self.hochschule,
                'beruf': self.beruf,
                'berufsfeld': self.berufsfeld,
                'geschlecht': self.geschlecht,
                'familienstand': self.familienstand,
                'kinder': self.kinder,
                'partei': self.partei,
                'land': self.land,
                'bio_url': self.bio_url,
                'bio': self.bio,
                'wissenswertes': self.wissenswertes,
                'homepage_url': self.homepage_url,
                'telefon': self.telefon,
                'angaben': self.angaben,
                'foto_url': self.foto_url,
                'foto_copyright': self.foto_copyright,
                'reden_plenum_url': self.reden_plenum_url,
                'reden_plenum_rss_url': self.reden_plenum_rss_url,
                'awatch_url': self.awatch_url,
                'twitter_url': self.twitter_url,
                'facebook_url': self.facebook_url,
                'rollen': [r.to_ref() for r in self.rollen],
                'created_at': self.created_at,
                'updated_at': self.updated_at
            }
        return data

    def to_ref(self):
        return {
                'id': self.id,
                'name': self.name,
                'slug': self.slug
                }

