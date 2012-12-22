import re
from hashlib import sha1
from datetime import datetime
import logging

import sqlaload as sl

log = logging.getLogger(__name__)


def extend_position(engine, table, data):
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
            data['source_url'].encode('utf-8')).hexdigest()
    data['hash'] = hash[:10]
    sl.upsert(engine, table, data, unique=['id'])


def extend_positions(engine, source_url):
    log.info("Amending positions ...")
    table = sl.get_table(engine, 'position')
    for data in sl.find(engine, table, source_url=source_url):
        extend_position(engine, table, data)

