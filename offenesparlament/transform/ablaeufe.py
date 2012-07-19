import logging

import sqlaload as sl

from offenesparlament.core import etl_engine
from offenesparlament.core import master_data

log = logging.getLogger(__name__)

def extend_ablaeufe(engine, master):
    log.info("Amending ablaeufe ...")
    Ablauf = sl.get_table(engine, 'ablauf')
    typen = [(t.get('typ'), t.get('class')) for t in master['ablauf_typ']]
    typen = dict(typen)
    for data in sl.distinct(engine, Ablauf, 'typ'):
        klass = typen.get(data.get('typ'))
        sl.upsert(engine, Ablauf, {'typ': data.get('typ'),
                         'class': klass}, 
                         unique=['typ'])

if __name__ == '__main__':
    engine = etl_engine()
    print "DESTINATION", engine
    extend_ablaeufe(engine, master_data())
