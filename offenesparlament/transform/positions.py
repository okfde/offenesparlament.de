import sys
import re
from hashlib import sha1
from datetime import datetime
import logging

import sqlaload as sl

from offenesparlament.core import etl_engine


log = logging.getLogger(__name__)


def extend_position(engine, data):
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
            data['ablauf_id'].encode('utf-8')).hexdigest()
    data['hash'] = hash[:10]
    sl.upsert(engine,
            sl.get_table(engine, 'position'),
            data, unique=['id'])
    return data


def extend_positions(engine):
    log.info("Amending positions ...")
    Position = sl.get_table(engine, 'position')
    for i, data in enumerate(sl.find(engine, Position)):
        if i % 1000 == 0:
            sys.stdout.write('.')
            sys.stdout.flush()
        extend_position(engine, data)

if __name__ == '__main__':
    engine = etl_engine()
    print "DESTINATION", engine
    extend_positions(engine)
