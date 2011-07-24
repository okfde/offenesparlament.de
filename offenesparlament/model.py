from datetime import datetime
from offenesparlament.core import db


class NewsItem(db.Model):
    __tablename__ = 'news_item'

    id = db.Column(db.Integer, primary_key=True)
    source_url = db.Column(db.Unicode)
    title = db.Column(db.Unicode)
    text = db.Column(db.UnicodeText)
    date = db.Column(db.DateTime)
    image_url = db.Column(db.Unicode)
    image_copyright = db.Column(db.Unicode)
    image_changed_at = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow)

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

class Gremium(db.Model):
    __tablename__ = 'gremium'

    id = db.Column(db.Integer, primary_key=True)
    vorsitz_id = db.Column(db.Integer, db.ForeignKey('person.id'))
    stellv_vorsitz_id = db.Column(db.Integer, db.ForeignKey('person.id'))
    source_url = db.Column(db.Unicode)
    rss_url = db.Column(db.Unicode)
    name = db.Column(db.Unicode)
    url = db.Column(db.Unicode)
    key = db.Column(db.Unicode)
    type = db.Column(db.Unicode)
    aufgabe = db.Column(db.Unicode)
    date = db.Column(db.DateTime)
    image_url = db.Column(db.Unicode)
    image_copyright = db.Column(db.Unicode)
    
    zuweisungen = db.relationship('Zuweisung', backref='gremium', 
            lazy='dynamic')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow)

class Person(db.Model):
    __tablename__ = 'person'

    id = db.Column(db.Integer, primary_key=True)
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
    homepage_url = db.Column(db.Unicode)
    telefon = db.Column(db.Unicode)
    homepage_url = db.Column(db.Unicode)
    angaben = db.Column(db.Unicode)
    foto_url = db.Column(db.Unicode)
    foto_copyright = db.Column(db.Unicode)
    reden_plenum_url = db.Column(db.Unicode)
    reden_plenum_rss_url = db.Column(db.Unicode)
    twitter_url = db.Column(db.Unicode)
    facebook_url = db.Column(db.Unicode)

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
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow)

class Rolle(db.Model):
    __tablename__ = 'rolle'

    id = db.Column(db.Integer, primary_key=True)
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'))
    mdb_id = db.Column(db.Unicode)
    status = db.Column(db.Unicode)
    funktion = db.Column(db.Unicode)
    fraktion = db.Column(db.Unicode)
    gewaehlt = db.Column(db.Unicode)
    rolle = db.Column(db.Unicode)
    land = db.Column(db.Unicode)
    austritt = db.Column(db.DateTime)
    
    wahlkreis_id = db.Column(db.Integer, db.ForeignKey('wahlkreis.id'))
    
    beitraege = db.relationship('Beitrag', backref='rolle',
                           lazy='dynamic')

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow)

class Postleitzahl(db.Model):
    __tablename__ = 'postleitzahl'
    
    plz = db.Column(db.Unicode, primary_key=True)
    wahlkreis_id = db.Column(db.Integer, db.ForeignKey('wahlkreis.id'))


class Wahlkreis(db.Model):
    __tablename__ = 'wahlkreis'

    id = db.Column(db.Integer, primary_key=True)
    nummer = db.Column(db.Unicode)
    name = db.Column(db.Unicode)
    url = db.Column(db.Unicode)

    mdbs = db.relationship('Rolle', backref='wahlkreis',
                           lazy='dynamic')
    plzs = db.relationship('Postleitzahl', backref='wahlkreis',
                           lazy='dynamic')

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow)


schlagworte = db.Table('schlagworte',
    db.Column('schlagwort_id', db.Integer, db.ForeignKey('schlagwort.id')),
    db.Column('ablauf_id', db.Integer, db.ForeignKey('ablauf.id'))
)

class Schlagwort(db.Model):
    __tablename__ = 'schlagwort'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode())

class Dokument(db.Model):
    __tablename__ = 'dokument'
    
    id = db.Column(db.Integer, primary_key=True)
    nummer = db.Column(db.Unicode())
    hrsg = db.Column(db.Unicode())
    typ = db.Column(db.Unicode())
    link = db.Column(db.Unicode())
    
    referenzen = db.relationship('Referenz', backref='dokument',
                           lazy='dynamic')
    
    ablaeufe = db.relationship('Ablauf', backref='dokument',
                           lazy='dynamic')
    
    beschluesse = db.relationship('Beschluss', backref='dokument',
                           lazy='dynamic')

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow)

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


class Zuweisung(db.Model):
    __tablename__ = 'zuweisung'

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Unicode())
    federfuehrung = db.Column(db.Boolean())
    
    gremium_id = db.Column(db.Integer, db.ForeignKey('gremium.id'))
    position_id = db.Column(db.Integer, db.ForeignKey('position.id'))

class Beitrag(db.Model):
    __tablename__ = 'beitrag'

    id = db.Column(db.Integer, primary_key=True)
    seite = db.Column(db.Unicode())
    art = db.Column(db.Unicode())
    
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'))
    rolle_id = db.Column(db.Integer, db.ForeignKey('rolle.id'))
    position_id = db.Column(db.Integer, db.ForeignKey('position.id'))

class Beschluss(db.Model):
    __tablename__ = 'beschluss'

    id = db.Column(db.Integer, primary_key=True)
    dokument_text = db.Column(db.Unicode())
    tenor = db.Column(db.Boolean())
    seite = db.Column(db.Boolean())
    
    dokument_id = db.Column(db.Integer, db.ForeignKey('dokument.id'))
    position_id = db.Column(db.Integer, db.ForeignKey('position.id'))

class Position(db.Model):
    __tablename__ = 'position'

    id = db.Column(db.Integer, primary_key=True)
    zuordnung = db.Column(db.Unicode())
    urheber = db.Column(db.Unicode())
    fundstelle = db.Column(db.Unicode())
    fundstelle_url = db.Column(db.Unicode())
    date = db.Column(db.DateTime())
    quelle = db.Column(db.Unicode())
    typ = db.Column(db.Unicode())
    
    ablauf_id = db.Column(db.Integer, db.ForeignKey('ablauf.id'))
    dokument_id = db.Column(db.Integer, db.ForeignKey('dokument.id'))
    
    zuweisungen = db.relationship('Zuweisung', backref='position', 
            lazy='dynamic')

    beschluesse = db.relationship('Beschluss', backref='position', 
            lazy='dynamic')
    
    beitraege = db.relationship('Beitrag', backref='position',
                           lazy='dynamic')

class Ablauf(db.Model):
    __tablename__ = 'ablauf'

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.Unicode())
    source_url = db.Column(db.Unicode())
    wahlperiode = db.Column(db.Unicode())
    typ = db.Column(db.Unicode())
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
    
    dokument_id = db.Column(db.Integer, db.ForeignKey('dokument.id'))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow)
    
    schlagworte = db.relationship('Schlagwort', 
        secondary=schlagworte,
        backref=db.backref('ablaeufe', lazy='dynamic'))
    
    positionen = db.relationship('Position', backref='ablauf',
                           lazy='dynamic')


db.create_all()

