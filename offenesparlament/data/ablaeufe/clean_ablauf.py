import logging
import sqlaload as sl

from offenesparlament.data.lib.reference import resolve_type, \
    resolve_stage, BadReference

log = logging.getLogger(__name__)

def clean_ablauf(engine, data):
    try:
        table = sl.get_table(engine, 'ablauf')
        data['class'] = resolve_type(data.get('typ'))
        data['stage'] = resolve_stage(data.get('stand'))
        d = {'class': data['class'], 
             'stage': data['stand'],
             'source_url': data['source_url']}
        sl.upsert(engine, table, d, unique=['source_url'])
    except BadReference:
        pass
