import logging

import sqlaload as sl

from offenesparlament.core import db
from offenesparlament.model.util import to_date
from offenesparlament.model import Stimme, Abstimmung, Person

log = logging.getLogger(__name__)


def load_abstimmung(engine, source_url):
    table = sl.get_table(engine, 'abstimmung')
    stimmen = list(sl.find(engine, table, source_url=source_url,
        matched=True))
    if not len(stimmen):
        log.error("No reconciled votes, signals deeper trouble?")
        return
    thema = stimmen[0].get('subject')
    abst = Abstimmung.query.filter_by(thema=thema).first()
    if abst is None:
        abst = Abstimmung()
        abst.thema = thema
        abst.datum = to_date(stimmen[0].get('date'))
    db.session.add(abst)
    db.session.flush()
    for stimme_ in stimmen:
        person = Person.query.filter_by(
            fingerprint=stimme_.get('fingerprint')).first()
        if person is None:
            continue
        stimme = Stimme.query.filter_by(
            abstimmung=abst).filter_by(
            person=person).first()
        if stimme is not None:
            continue
        stimme = Stimme()
        stimme.entscheidung = stimme_['vote']
        stimme.person = person
        stimme.abstimmung = abst
        db.session.add(stimme)
    db.session.commit()

