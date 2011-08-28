import sys
import re
from hashlib import sha1
from datetime import datetime
import logging

from webstore.client import URL as WebStore

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.NOTSET)

UNIQUE = ['fundstelle', 'urheber', 'ablauf_source_url']

def extend_positions(db):
    log.info("Amending positions ...")
    Position = db['position']
    for data in Position:
        dt, rest = data['fundstelle'].split("-", 1)
        data['date'] = datetime.strptime(dt.strip(), "%d.%m.%Y").isoformat()
        if ',' in data['urheber']:
            typ, quelle = data['urheber'].split(',', 1)
            data['quelle'] = re.sub("^.*Urheber.*:", "", quelle).strip()
            data['typ'] = typ.strip()
        else:
            data['typ'] = data['urheber']

        br = 'Bundesregierung, '
        if br in data['urheber']:
            data['urheber'] = data['urheber'][len(br):]

        hash = sha1(data['fundstelle'].encode('utf-8') \
                + data['urheber'].encode('utf-8') + \
                data['ablauf_source_url'].encode('utf-8')).hexdigest()
        data['hash'] = hash[:7]
        Position.writerow(data, unique_columns=UNIQUE)

if __name__ == '__main__':
    assert len(sys.argv)==2, "Need argument: webstore-url!"
    db, _ = WebStore(sys.argv[1])
    print "DESTINATION", db
    extend_positions(db)
