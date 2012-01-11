#coding: utf-8
import logging
import json
from datetime import datetime
from collections import defaultdict

from flask import url_for
from pprint import pprint

from offenesparlament.core import db, app, solr
from offenesparlament.model import Abo, Position, Zitat
from offenesparlament.mailer import send_message

log = logging.getLogger(__name__)

def url_external(path):
    prefix = app.config.get('SITE_URL', 'http://offenesparlament.de')
    return prefix + path

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
    results = search(Position, abo.offset, abo.query)
    ablaeufe = defaultdict(list)
    for position in results:
        ablaeufe[position.ablauf].append(position)

    for ablauf, positionen in ablaeufe.items():
        msg = '[%s] %s (Ereignisse: ' % (ablauf.typ, ablauf.titel.replace('\n', ''))
        msg += ', '.join(set([p.typ.strip() for p in positionen if p.typ]))
        #for position in positionen:
        #    msg += ' * %s (%s, %s)\n' % (position.urheber,
        #            position.date.strftime('%d.%m.%Y'),
        #            position.zuordnung)
        msg += ')\nLink: %s\n' % url_external(url_for('ablauf',
            wahlperiode=ablauf.wahlperiode,
            key=ablauf.key))
        yield msg

def match_speeches(abo):
    results = search(Zitat, abo.offset, abo.query)
    #pprint(results)
    debatten = defaultdict(list)
    for zitat in results:
        pprint(zitat.to_dict())
        for dz in zitat.debatten_zitate:
            print dz
            if dz.debatte:
                debatten[dz.debatte].append(zitat)

    for debatte, zitate in debatten.items():
        msg = debatte.sitzung.titel + ': ' + debatte.titel
        msg = u'\nErwähnung von "%s" durch: %s' % (
                abo.query, ', '.join([z.sprecher for z in zitate]))
        msg += '\nLink: %s\n' % url_external(url_for('debatte',
            wahlperiode=debatte.sitzung.wahlperiode,
            nummer=debatte.sitzung.nummer,
            debatte=debatte.nummer))
        yield msg

def format_matching_abos(abos):
    unsubs = []
    for abo in abos:
        unsub = "* '" + abo.query
        unsub += "' - abmelden: " + url_external("/unsubscribe/" + str(abo.id))
        unsubs.append(unsub)
    return '\n'.join(unsubs)


def notify_email(email):
    abos = db.session.query(Abo).filter_by(activation_code=None)
    abos = abos.filter_by(email=email).all()
    matching_abos = []
    results = []
    new_offset = datetime.utcnow()
    for abo in abos:
        abo_results = []
        #if abo.include_activity:
        #    abo_results.extend(match_positions(abo))
        #if abo.include_speeches:
        abo_results.extend(match_speeches(abo))
        if len(abo_results):
            matching_abos.append(abo)
            results.extend(abo_results)
        abo.offset = new_offset

    if not len(results):
        return

    message = BASE_MESSAGE % ('\n'.join(results), 
            format_matching_abos(matching_abos))
    send_message(email, 
        u"Aktuelles im Parlament",
        message)
    #db.session.commit()


def notify():
    for (email,) in db.session.query(Abo.email).distinct():
        try:
            notify_email(email)
        except Exception, e:
            log.error("Delivery failure: %s", email)
            log.exception(e)



ACTIVATION_MESSAGE = u"""
Guten Tag, 

auf der Seite offenesparlament.de haben Sie Benachrichtigungen zum Thema
%s abonniert. Um diesen Dienst zu aktivieren ist eine Bestätigung Ihrer
E-Mail-Adresse durch den untenstehenden Link notwendig. Wenn Sie keine 
Nachrichten erhalten wollen ist keine weitere Reaktion notwendig.

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


