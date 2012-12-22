import re
import sys
import logging

import sqlaload as sl

from offenesparlament.core import etl_engine

DRS_MATCH = "- Drucksachen? (%s/\\d{1,6})([,;/]? (%s/\\d{1,6}))* -"

log = logging.getLogger(__name__)

UNIQUE = ['__id__']

def extend_speeches(engine, wahlperiode=17):
    log.info("Amending speeches with DRS ...")
    drs_match = re.compile(DRS_MATCH % (wahlperiode, wahlperiode))
    Speech = sl.get_table(engine, 'speech')
    SpeechDocument = sl.get_table(engine, 'speech_document')
    for i, data in enumerate(sl.find(engine, Speech)):
        if data.get('type') != 'chair':
            continue
        if i % 1000 == 0:
            sys.stdout.write('.')
            sys.stdout.flush()
        m = drs_match.search(data.get('text'))
        if m is None:
            continue
        for i, grp in enumerate(m.groups()):
            if grp and '/' in grp:
                wp, nummer = grp.split('/', 1)
                sl.upsert(engine, SpeechDocument, {
                    'group': i,
                    'sequence': data['sequence'],
                    'sitzung': data['sitzung'],
                    'wahlperiode': wahlperiode,
                    'dok_nummer': nummer},
                    unique=['sequence', 'sitzung', 'wahlperiode', 'group'])

