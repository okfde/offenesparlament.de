#coding: utf-8
import logging
import json
from datetime import datetime
from collections import defaultdict

from flask import url_for
from colander import MappingSchema, SchemaNode, String
from colander import Email, Length, Boolean

from offenesparlament.core import db, app, solr
from offenesparlament.model import Abo, Position, Zitat
from offenesparlament.lib.mailer import send_message

log = logging.getLogger(__name__)


class AboSchema(MappingSchema):
    query = SchemaNode(String(), validator=Length(min=4))
    email = SchemaNode(String(), validator=Email())
    include_activity = SchemaNode(Boolean(), missing=False)
    include_speeches = SchemaNode(Boolean(), missing=False)


def url_external(path):
    prefix = app.config.get('SITE_URL', 'http://offenesparlament.de')
    return prefix + path


def send_activation(abo):
    try:
        url = url_external(url_for('abo.activate', key=abo.activation_code))
        message = ACTIVATION_MESSAGE % (abo.query, url)
        send_message(abo.email, u"Bestätigen Sie Ihr Themen-Abo", message)
    except Exception, e:
        log.exception(e)


def search(entity, offset, query):
    if offset is not None:
        offset = offset.isoformat().rsplit(".")[0] + "Z"
    else:
        offset = '*'
    name = entity.__name__.lower()
    results = solr().raw_query(q=query,
        fq=["+index_type:%s" % name,
            "+date:[%s TO *]" % offset],
        sort="date desc", rows=1000, wt="json", fl="id")
    results = json.loads(results)
    results = [d.get('id') for d in \
               results.get('response', {}).get('docs', [])]
    if len(results):
        results = db.session.query(entity).filter(entity.id.in_(results)).all()
    return results


def match_positions(abo):
    return search(Position, abo.offset, abo.query)


def match_speeches(abo):
    return search(Zitat, abo.offset, abo.query)


def format_activities(results):
    ablaeufe = defaultdict(list)
    for position in results:
        ablaeufe[position.ablauf].append(position)

    for ablauf, positionen in ablaeufe.items():
        msg = '[%s] %s (Ereignisse: ' % (ablauf.typ, ablauf.titel.replace('\n', ''))
        msg += ', '.join(set([p.typ.strip() for p in positionen if p.typ]))
        msg += ')\nLink: %s\n' % url_external(url_for('ablauf.view',
            wahlperiode=ablauf.wahlperiode,
            key=ablauf.key))
        yield msg


def format_speeches(results):
    debatten = defaultdict(list)
    for zitat in results:
        debatten[zitat.debatte].append(zitat)

    for debatte, zitate in debatten.items():
        msg = debatte.sitzung.titel + ': ' + debatte.titel
        msg = u'\nErwähnung: %s' % (', '.join([z.sprecher for z in zitate]))
        msg += '\nLink: %s\n' % url_external(url_for('debatte.view',
            wahlperiode=debatte.sitzung.wahlperiode,
            nummer=debatte.sitzung.nummer,
            debatte=debatte.nummer))
        yield msg


def format_matching_abos(abos):
    unsubs = []
    for abo in abos:
        unsub = "* '" + abo.query
        unsub += "' - abmelden: " + url_external(url_for('abo.terminate',
            id=str(abo.id), email=abo.email))
        unsubs.append(unsub)
    return '\n'.join(unsubs)


def notify_email(email):
    abos = db.session.query(Abo).filter_by(activation_code=None)
    abos = abos.filter_by(email=email).all()
    matching_abos = []
    activities = set()
    speeches = set()
    new_offset = datetime.utcnow()
    for abo in abos:
        before_len = len(activities)+len(speeches)
        if abo.include_activity:
            activities = activities.union(match_positions(abo))
        if abo.include_speeches:
            speeches = speeches.union(match_speeches(abo))
        if len(activities)+len(speeches) > before_len:
            matching_abos.append(abo)
            abo.offset = new_offset
    
    results = []
    if len(activities):
        results.append(u'\nABLÄUFE UND DRUCKSACHEN\n')
        results.extend(format_activities(activities))

    if len(speeches):
        results.append(u'\nDEBATTEN IM PLENUM\n')
        results.extend(format_speeches(speeches))

    if len(results):
        message = BASE_MESSAGE % ('\n'.join(results), 
            format_matching_abos(matching_abos))
        send_message(email, 
            u"Aktuelles im Parlament",
            message)
    db.session.commit()


def notify():
    for (email,) in db.session.query(Abo.email).distinct():
        try:
            notify_email(email)
        except Exception, e:
            log.error("Delivery failure: %s", email)
            log.exception(e)



ACTIVATION_MESSAGE = u"""
Guten Tag, 

auf OffenesParlament haben Sie Benachrichtigungen zum Thema '%s'
abonniert. Um diesen Dienst zu aktivieren, ist eine Bestätigung Ihrer
E-Mail-Adresse durch den notwendig. Bitte besuchen Sie dazu den unten
genannten Link. Wenn Sie keine Nachrichten erhalten wollen, dann ist
keine weitere Reaktion notwendig.

%s

--
Beste Grüße, 

 OffenesParlament.de
"""

BASE_MESSAGE = u"""
Guten Tag,

die folgenden aktuellen Ereignisse entsprechen Ihren Suchkriterien:

%s

--
Diese Zusammenstellung basiert auf den folgenden Abonnements:

%s

Beste Grüße, 

 OffenesParlament.de
"""


