import logging

from nkclient import NKNoMatch, NKInvalid
import sqlaload as sl

from offenesparlament.core import etl_engine, nk_types

log = logging.getLogger(__name__)

_TYPES_CACHE = {}

def match_type(typ):
    nkt = nk_types()
    if typ not in _TYPES_CACHE:
        try:
            obj = nkt.lookup(typ)
        except NKInvalid, inv:
            obj = inv
        except NKNoMatch, nm:
            obj = nm
        _TYPES_CACHE[typ] = obj
    obj = _TYPES_CACHE[typ]
    if isinstance(obj, (NKInvalid, NKNoMatch)):
        return None
    return obj.value

def extend_ablaeufe(engine):
    log.info("Amending ablaeufe ...")
    Ablauf = sl.get_table(engine, 'ablauf')
    for data in sl.distinct(engine, Ablauf, 'typ'):
        klass = match_type(data.get('typ'))
        sl.upsert(engine, Ablauf, {'typ': data.get('typ'),
                         'class': klass}, 
                         unique=['typ'])

if __name__ == '__main__':
    engine = etl_engine()
    print "DESTINATION", engine
    extend_ablaeufe(engine)
