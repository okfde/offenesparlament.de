#coding: utf-8
from datetime import datetime
import re
import uuid
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

    gremium_id = db.Column(db.Integer, db.ForeignKey('gremium.id'))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'source_url': self.source_url,
            'title': self.title,
            'text': self.text,
            'date': self.date,
            'image_url': self.image_url,
            'image_copyright': self.image_copyright,
            'image_changed_at': self.image_changed_at,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'gremium': self.gremium.to_ref()
            }

    def to_ref(self):
        return {
            'id': self.id,
            'source_url': self.source_url,
            'title': self.title,
            'gremium_id': self.gremium.id
            }

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
    typ = db.Column(db.Unicode)
    aufgabe = db.Column(db.Unicode)
    image_url = db.Column(db.Unicode)
    image_copyright = db.Column(db.Unicode)

    zuweisungen = db.relationship('Zuweisung', backref='gremium', 
            lazy='dynamic')
    news = db.relationship('NewsItem', backref='gremium',
                           lazy='dynamic')

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'vorsitz': self.vorsitz.to_ref() if \
                    self.vorsitz else None,
            'stellv_vorsitz': self.stellv_vorsitz.to_ref() if \
                    self.stellv_vorsitz else None,
            'source_url': self.source_url,
            'rss_url': self.rss_url,
            'name': self.name,
            'url': self.url,
            'key': self.key,
            'typ': self.typ,
            'aufgabe': self.aufgabe,
            'image_url': self.image_url,
            'image_copyright': self.image_copyright,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'obleute': [m.to_ref() for m in self.obleute],
            'mitglieder': [m.to_ref() for m in self.mitglieder],
            'stellvertreter': [m.to_ref() for m in self.stellvertreter],
            }

    def to_ref(self):
        return {
            'id': self.id,
            'source_url': self.source_url,
            'name': self.name,
            'key': self.key
            }


class Person(db.Model):
    __tablename__ = 'person'

    id = db.Column(db.Integer, primary_key=True)
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
    
    zitate = db.relationship('Zitat', backref='person',
                           lazy='dynamic')
    
    stimmen = db.relationship('Stimme', backref='person',
                           lazy='dynamic')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow)
    
    @property
    def name(self):
        name = "%s %s %s" % (self.titel if self.titel else '', \
                self.vorname, self.nachname)
        if self.ort and len(self.ort):
            name += " (%s)" % self.ort
        return name.strip()

    @property
    def bio_teaser(self):
        if not self.bio:
            return ""
        return re.split("(\n|<br)", self.bio)[0]

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


class Rolle(db.Model):
    __tablename__ = 'rolle'

    id = db.Column(db.Integer, primary_key=True)
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

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow)

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


class Postleitzahl(db.Model):
    __tablename__ = 'postleitzahl'

    plz = db.Column(db.Unicode, primary_key=True)
    wahlkreis_id = db.Column(db.Integer, db.ForeignKey('wahlkreis.id'))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow)


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

    def to_ref(self):
        return {
                'id': self.id,
                'nummer': self.nummer,
                'name': self.name,
                'url': self.url,
            }

    def to_dict(self):
        data = self.to_ref()
        data.update({
            'mdbs': [m.to_ref() for m in self.mdbs],
            'plzs': [p.plz for p in self.plzs],
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            })
        return data


schlagworte = db.Table('schlagworte',
    db.Column('schlagwort_id', db.Integer, db.ForeignKey('schlagwort.id')),
    db.Column('ablauf_id', db.Integer, db.ForeignKey('ablauf.id'))
)


class Schlagwort(db.Model):
    __tablename__ = 'schlagwort'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode())

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


class Zuweisung(db.Model):
    __tablename__ = 'zuweisung'

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Unicode())
    federfuehrung = db.Column(db.Boolean())

    gremium_id = db.Column(db.Integer, db.ForeignKey('gremium.id'))
    position_id = db.Column(db.Integer, db.ForeignKey('position.id'))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow)

    def to_ref(self):
        return {
                'id': self.id,
                'text': self.text,
                'federfuehrung': self.federfuehrung,
                'gremium': self.gremium.key if self.gremium else None,
                'position': self.position.id if self.position else None
                }

    def to_dict(self):
        data = self.to_ref()
        data.update({
            'gremium': self.gremium.to_ref(),
            'position': self.position.to_ref(),
            'created_at': self.created_at,
            'updated_at': self.updated_at
            })
        return data


class Beitrag(db.Model):
    __tablename__ = 'beitrag'

    id = db.Column(db.Integer, primary_key=True)
    seite = db.Column(db.Unicode())
    art = db.Column(db.Unicode())

    person_id = db.Column(db.Integer, db.ForeignKey('person.id'))
    rolle_id = db.Column(db.Integer, db.ForeignKey('rolle.id'))
    position_id = db.Column(db.Integer, db.ForeignKey('position.id'))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow)

    def to_ref(self):
        return {
                'id': self.id,
                'seite': self.seite,
                'art': self.art,
                'position': self.position.id,
                'rolle': self.rolle.id if self.rolle else None,
                'person': self.person.id if self.person else None
                }

    def to_dict(self):
        data = self.to_ref()
        data.update({
            'person': self.person.to_ref() if self.person else None,
            'rolle': self.rolle.to_ref() if self.rolle else None,
            'position': self.position.to_ref(),
            'created_at': self.created_at,
            'updated_at': self.updated_at
            })
        return data


class Beschluss(db.Model):
    __tablename__ = 'beschluss'

    id = db.Column(db.Integer, primary_key=True)
    dokument_text = db.Column(db.Unicode())
    tenor = db.Column(db.Unicode())
    seite = db.Column(db.Unicode())

    position_id = db.Column(db.Integer, db.ForeignKey('position.id'))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow)

    def to_ref(self):
        return {
                'id': self.id,
                'dokument_text': self.dokument_text,
                'tenor': self.tenor,
                'seite': self.seite,
                'position': self.position.id
                }

    def to_dict(self):
        data = self.to_ref()
        data.update({
            'dokument': self.dokument.to_ref(),
            'position': self.position.to_ref(),
            'created_at': self.created_at,
            'updated_at': self.updated_at
            })
        return data


class Position(db.Model):
    __tablename__ = 'position'

    id = db.Column(db.Integer, primary_key=True)
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

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow)

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


class Ablauf(db.Model):
    __tablename__ = 'ablauf'

    id = db.Column(db.Integer, primary_key=True)
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
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow)
    
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


class Sitzung(db.Model):
    __tablename__ = 'sitzung'

    id = db.Column(db.Integer, primary_key=True)
    wahlperiode = db.Column(db.Integer())
    nummer = db.Column(db.Integer())
    titel = db.Column(db.Unicode())
    date = db.Column(db.DateTime())
    source_url = db.Column(db.Unicode())

    debatten = db.relationship('Debatte', backref='sitzung',
                           lazy='dynamic', order_by='Debatte.nummer.asc()')

    zitate = db.relationship('Zitat', backref='sitzung',
                           lazy='dynamic', order_by='Zitat.sequenz.asc()')

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow)

    def to_ref(self):
        return {
            'id': self.id,
            'wahlperiode': self.wahlperiode,
            'nummer': self.nummer,
            'date': self.date,
            'titel': self.titel
            }

    def to_dict(self):
        data = self.to_ref()
        data.update({
            'debatten': [d.to_ref() for d in self.debatten],
            'created_at': self.created_at,
            'updated_at': self.updated_at
            })
        return data


class Debatte(db.Model):
    __tablename__ = 'debatte'

    id = db.Column(db.Integer, primary_key=True)
    tops = db.Column(db.Unicode())
    nummer = db.Column(db.Integer())
    titel = db.Column(db.Unicode())
    text = db.Column(db.Unicode())

    sitzung_id = db.Column(db.Integer, db.ForeignKey('sitzung.id'))

    zitate = db.relationship('Zitat', backref='debatte',
                           lazy='dynamic', order_by='Zitat.sequenz.asc()')

    positionen = db.relationship('Position', backref='debatte',
                           lazy='dynamic')

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow)

    def to_ref(self):
        return {
            'id': self.id,
            'nummer': self.nummer,
            'titel': self.titel
            }

    def to_dict(self):
        data = self.to_ref()
        data.update({
            'sitzung': self.sitzung.to_ref() if self.sitzung else None,
            'text': self.text,
            'positionen': [p.to_ref() for p in self.positionen],
            'created_at': self.created_at,
            'updated_at': self.updated_at
            })
        return data


class Zitat(db.Model):
    __tablename__ = 'zitat'

    id = db.Column(db.Integer, primary_key=True)
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

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow)

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


class Abstimmung(db.Model):
    __tablename__ = 'abstimmung'

    id = db.Column(db.Integer, primary_key=True)
    thema = db.Column(db.Unicode())
    datum = db.Column(db.DateTime, default=datetime.utcnow)
    
    stimmen = db.relationship('Stimme', backref='abstimmung',
                              lazy='dynamic')
    
    @property
    def titel(self):
        titel = self.thema
        s1 = titel.split(u'über', 1)
        s2 = titel.split(u'Über', 1)
        if len(s1) > 1:
            titel = s1[-1]
        elif len(s2) > 1:
            titel = s2[-1]

        titel = titel.split('Drs', 1)[0]
        titel = titel.rstrip(';- .')

        t = titel.split()
        t[0] = t[0].capitalize()
        titel = ' '.join(t)
        return titel

    def to_ref(self):
        return {
            'id': self.id,
            'thema': self.thema,
            }

    def to_dict(self):
        data = self.to_ref()
        data.update({
            'stimmen': [s.to_ref() for s in self.stimmen],
            'created_at': self.created_at,
            'updated_at': self.updated_at
            })
        return data


class Stimme(db.Model):
    __tablename__ = 'stimme'

    id = db.Column(db.Integer, primary_key=True)
    entscheidung = db.Column(db.Unicode())

    person_id = db.Column(db.Integer, db.ForeignKey('person.id'), 
            nullable=True)
    abstimmung_id = db.Column(db.Integer, db.ForeignKey('abstimmung.id'), 
            nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow)

    def to_ref(self):
        return {
            'id': self.id,
            'abstimmung': self.abstimmung.thema,
            'person': self.person.to_ref(),
            }

    def to_dict(self):
        data = self.to_ref()
        data.update({
            'abstimmung': self.abstimmung.to_ref(),
            'person': self.person.to_ref(),
            'created_at': self.created_at,
            'updated_at': self.updated_at
            })
        return data


def make_token():
    return uuid.uuid4().get_hex()[15:]

class Abo(db.Model):
    __tablename__ = 'abo'

    id = db.Column(db.Integer, primary_key=True)

    query = db.Column(db.Unicode())
    email = db.Column(db.Unicode())
    offset = db.Column(db.DateTime, default=datetime.utcnow)
    activation_code = db.Column(db.Unicode(), default=make_token)
    include_activity = db.Column(db.Boolean)
    include_speeches = db.Column(db.Boolean)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow)



current_schlagwort = db.Table('current_schlagwort', db.metadata,
        db.Column('schlagwort', db.Unicode),
        db.Column('num', db.Integer),
        db.Column('period', db.Unicode))

period_sachgebiet = db.Table('period_sachgebiet', db.metadata,
        db.Column('sachgebiet', db.Unicode),
        db.Column('num', db.Integer),
        db.Column('period', db.Unicode))

person_schlagwort = db.Table('person_schlagwort', db.metadata,
        db.Column('person_id', db.Integer),
        db.Column('schlagwort', db.Unicode),
        db.Column('num', db.Integer))

db.create_all()
