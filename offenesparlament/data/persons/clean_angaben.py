#coding: utf-8
import logging
from lxml import html

import sqlaload as sl

log = logging.getLogger(__name__)

LEVELS = ('Stufe 1', 'Stufe 2', 'Stufe 3')

def parse_angaben(engine, data):
    if not data.get('angaben'):
        return
    snippet = '<x>' + data['angaben'] + '</x>'
    doc = html.fragment_fromstring(snippet)
    table = sl.get_table(engine, 'angaben')
    data = {'source_url': data['source_url']}
    wrapped_name = False
    for el in doc:
        if el.tag == 'h3':
            wrapped_name = False
            data['section'] = el.text.split('. ', 1)[-1]
        elif el.tag == 'strong' or not el.text or not el.get('class'):
            continue
        elif 'voa_abstand' in el.get('class') or wrapped_name:
            client = el.text
            if wrapped_name:
                client = data['client'] + ' ' + client
            data['client'] = client
            client.strip().strip(',')
            els = client.rsplit(',', 2)
            if len(els) == 3:
                wrapped_name = False
                data['client_name'] = els[0].strip()
                data['client_city'] = els[1].strip()
            else:
                wrapped_name = True
                continue
        else:
            data['service'] = el.text
            data['level'] = 'Stufe 0'
            for name in LEVELS:
                if name.lower() in data['service'].lower():
                    data['level'] = name
            sl.upsert(engine, table, data,
                ['source_url', 'section', 'client', 'service'])

