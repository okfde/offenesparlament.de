import logging
from threading import Lock

from nkclient import NKDataset, NKValue
from nkclient import NKNoMatch, NKInvalid

from offenesparlament.core import app

log = logging.getLogger(__name__)

DATASETS = {}
VALUES = {}
LOCK = Lock()

class BadReference(Exception):
    pass

class InvalidReference(BadReference):
    pass

def dataset(name):
    if not name in DATASETS:
        DATASETS[name] = NKDataset(name, api_key=app.config['NOMENKLATURA_API_KEY'])
        for value in DATASETS[name].values():
            VALUES[(name, value.value.lower())] = value
        for link in DATASETS[name].links():
            if link.is_invalid:
                VALUES[(name, link.key.lower())] = \
                    NKInvalid({'dataset': link.dataset, 'key': link.key})
            elif link.is_matched:
                VALUES[(name, link.key.lower())] = \
                    NKValue(DATASETS[name], link.value)
    return DATASETS[name]

def resolve(dataset_name, key):
    LOCK.acquire()
    try:
        cache_tpl = (dataset_name, key.lower())
        if cache_tpl not in VALUES:
            resolver = dataset(dataset_name)
            try:
                obj = resolver.lookup(key)
            except NKInvalid, inv:
                obj = inv
            except NKNoMatch, nm:
                obj = nm
            VALUES[cache_tpl] = obj
        obj = VALUES[cache_tpl]
        if isinstance(obj, NKInvalid):
            raise InvalidReference()
        if isinstance(obj, NKNoMatch):
            raise BadReference()
        return obj.value
    finally:
        LOCK.release()

def resolve_type(key):
    return resolve(app.config['NOMENKLATURA_TYPES_DATASET'], key)

def resolve_person(key):
    return resolve(app.config['NOMENKLATURA_PERSONS_DATASET'], key)




