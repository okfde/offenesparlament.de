import sys
import logging
from pprint import pprint
from datetime import datetime
from collections import defaultdict

import sqlaload as sl

from offenesparlament.core import etl_engine
from offenesparlament.transform.drs import drucksachen

log = logging.getLogger(__name__)

def cache_abstimmungen(engine):
    Abstimmung = sl.get_table(engine, 'abstimmung')
    data = defaultdict(dict)
    for e in sl.distinct(engine, Abstimmung, 'subject', 'date'):
        data[e['date']][e['subject']] = set(drucksachen(e['subject']))
    return dict(data.items())


def extend_beschluesse(engine):
    log.info("Re-connecting beschluesse ...")
    abstimmungen = cache_abstimmungen(engine)
    #pprint(abstimmungen)
    Beschluss = sl.get_table(engine, 'beschluss')
    for data in sl.find(engine, Beschluss):
        date = data['fundstelle'].split(' ')[0]
        data['date'] = datetime.strptime(date, '%d.%m.%Y').isoformat()
        if not data['dokument_text']:
            continue
        if data['date'] in abstimmungen:
            abst = abstimmungen[data['date']]
            doks = set(data['dokument_text'].split(', '))
            for subject, adoks in abst.items():
                if len(doks & adoks):
                    print "MATCH", data['date'], doks, adoks


if __name__ == '__main__':
    engine = etl_engine()
    print "DESTINATION", engine
    extend_beschluesse(engine)
