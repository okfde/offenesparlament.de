import sys
import logging
from pprint import pprint
from datetime import datetime
from collections import defaultdict

from webstore.client import URL as WebStore

from offenesparlament.core import master_data
from offenesparlament.transform.drs import drucksachen

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.NOTSET)

def cache_abstimmungen(db):
    data = defaultdict(dict)
    q = db.query("SELECT DISTINCT subject, date FROM abstimmung;")
    for e in q:
        data[e['date']][e['subject']] = set(drucksachen(e['subject']))
    return dict(data.items())


def extend_beschluesse(db, master):
    log.info("Re-connecting beschluesse ...")
    abstimmungen = cache_abstimmungen(db)
    pprint(abstimmungen)
    Beschluss = db['beschluss']
    for data in Beschluss:
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
    assert len(sys.argv)==2, "Need argument: webstore-url!"
    db, _ = WebStore(sys.argv[1])
    print "DESTINATION", db
    extend_beschluesse(db, master_data())
