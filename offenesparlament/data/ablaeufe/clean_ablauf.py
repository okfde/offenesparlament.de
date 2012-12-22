import logging
import sqlaload as sl

from offenesparlament.data.lib.reference import resolve_type, \
    BadReference

log = logging.getLogger(__name__)

def clean_ablauf(engine, data):
    try:
        table = sl.get_table(engine, 'ablauf')
        data['class'] = resolve_type(data.get('typ'))
        d = {'class': data['class'], 'source_url': data['source_url']}
        sl.upsert(engine, table, d, unique=['source_url'])
    except BadReference:
        pass
