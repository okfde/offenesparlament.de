import sys
import re
from hashlib import sha1
from datetime import datetime
import logging

from webstore.client import URL as WebStore

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.NOTSET)

UNIQUE = ['__id__']

def extend_positions(db):
    log.info("Amending positions ...")
    Position = db['position']
    for i, data in enumerate(Position):
        if i % 1000 == 0:
            sys.stdout.write('.')
            sys.stdout.flush()
        dt, rest = data['fundstelle'].split("-", 1)
        data['date'] = datetime.strptime(dt.strip(), "%d.%m.%Y").isoformat()
        if ',' in data['urheber']:
            typ, quelle = data['urheber'].split(',', 1)
            data['quelle'] = re.sub("^.*Urheber.*:", "", quelle).strip()
            data['typ'] = typ.strip()
        else:
            data['typ'] = data['urheber']

        br = 'Bundesregierung, '
        if data['urheber'].startswith(br):
            data['urheber'] = data['urheber'][len(br):]

        data['fundstelle_doc'] = None
        if data['fundstelle_url'] and \
                'btp' in data['fundstelle_url']:
            data['fundstelle_doc'] = data['fundstelle_url']\
                    .rsplit('#',1)[0]

        hash = sha1(data['fundstelle'].encode('utf-8') \
                + data['urheber'].encode('utf-8') + \
                data['ablauf_source_url'].encode('utf-8')).hexdigest()
        data['hash'] = hash[:7]
        Position.writerow(data, unique_columns=UNIQUE,
                          bufferlen=2000)
    Position.flush()

def generate_beschluss_referenzen(db):
    log.info("Generating document references for 'beschluss'....")


if __name__ == '__main__':
    assert len(sys.argv)==2, "Need argument: webstore-url!"
    db, _ = WebStore(sys.argv[1])
    print "DESTINATION", db
    extend_positions(db)
