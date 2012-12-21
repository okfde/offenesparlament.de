import logging

import sqlaload as sl

from offenesparlament.core import db
from offenesparlament.model.util import to_date
from offenesparlament.model import Person, Rolle, Wahlkreis

log = logging.getLogger(__name__)

def load_person(engine, data):
    person = Person.query.filter_by(
            fingerprint=data.get('fingerprint')).first()
    if person is None:
        person = Person()

    person.slug = data.get('slug')
    person.fingerprint = data.get('fingerprint')
    person.source_url = data.get('source_url')
    person.mdb_id = data.get('mdb_id')
    person.vorname = data.get('vorname')
    person.nachname = data.get('nachname')
    person.adelstitel = data.get('adelstitel')
    person.titel = data.get('titel')
    person.ort = data.get('ort')
    person.geburtsdatum = data.get('geburtsdatum')
    person.religion = data.get('religion')
    person.hochschule = data.get('hochschule')
    person.beruf = data.get('beruf')
    person.berufsfeld = data.get('berufsfeld')
    person.geschlecht = data.get('geschlecht')
    person.familienstand = data.get('familienstand')
    person.kinder = data.get('kinder')
    person.partei = data.get('partei')
    person.land = data.get('land')
    person.bio_url = data.get('bio_url')
    person.bio = data.get('bio')
    person.wissenswertes = data.get('wissenswertes')
    person.homepage_url = data.get('homepage_url')
    person.telefon = data.get('telefon')
    person.homepage_url = data.get('homepage_url')
    person.angaben = data.get('angaben')
    person.foto_url = data.get('foto_url')
    person.foto_copyright = data.get('foto_copyright')
    person.reden_plenum_url = data.get('reden_plenum_url')
    person.reden_plenum_rss_url = data.get('reden_plenum_rss_url')
    person.twitter_url = data.get('twitter_url')
    person.facebook_url = data.get('facebook_url')
    person.awatch_url = data.get('awatch_url')
    db.session.add(person)
    db.session.flush()
    mdb_rolle = load_rollen(engine, person, data)
    #load_gremium_mitglieder(engine, person, mdb_rolle)
    db.session.commit()
    return person


def load_wahlkreis(engine, rolle, data):
    if data.get('wk_nummer'):
        wk = Wahlkreis.query.filter_by(
            nummer=data.get('wk_nummer')).first()
        if wk is None:
            wk = Wahlkreis()
        wk.nummer = data.get('wk_nummer')
        wk.name = data.get('wk_name')
        wk.url = data.get('wk_url')
        db.session.add(wk)
        return wk


def load_rollen(engine, person, data):
    _RolleSource = sl.get_table(engine, 'rolle')
    mdb_rolle = None
    for rdata in sl.find(engine, _RolleSource, fingerprint=data['fingerprint']):
        rolle = Rolle.query.filter_by(
                person=person,
                funktion=rdata.get('funktion'),
                ressort=rdata.get('ressort'),
                fraktion=rdata.get('fraktion'),
                land=rdata.get('land')).first()
        if rolle is None:
            rolle = Rolle()

        rolle.person = person
        rolle.mdb_id = rdata.get('mdb_id')
        rolle.status = rdata.get('status')
        rolle.funktion = rdata.get('funktion')
        rolle.fraktion = rdata.get('fraktion')
        rolle.gewaehlt = rdata.get('gewaehlt')
        rolle.ressort = rdata.get('ressort')
        rolle.land = rdata.get('land')
        rolle.austritt = to_date(rdata.get('austritt'))

        if rdata.get('mdb_id'):
            rolle.wahlkreis = load_wahlkreis(engine, rolle, data)
            mdb_rolle = rolle
        db.session.add(rolle)
    return mdb_rolle


