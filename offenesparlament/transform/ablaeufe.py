import logging

import sqlaload as sl

from offenesparlament.core import etl_engine
from offenesparlament.data.lib.reference import resolve_type, \
    BadReference

log = logging.getLogger(__name__)

def extend_ablaeufe(engine):
    log.info("Amending ablaeufe ...")
    Ablauf = sl.get_table(engine, 'ablauf')
    for data in sl.distinct(engine, Ablauf, 'typ'):
        try:
            klass = resolve_type(data.get('typ'))
            sl.upsert(engine, Ablauf, {'typ': data.get('typ'),
                             'class': klass}, 
                             unique=['typ'])
        except BadReference:
            pass

if __name__ == '__main__':
    engine = etl_engine()
    print "DESTINATION", engine
    extend_ablaeufe(engine)
