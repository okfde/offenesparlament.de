import logging

from nkclient import NKDataset
from nkclient import NKNoMatch, NKInvalid

from offenesparlament.core import app

log = logging.getLogger(__name__)

DATASETS = {}
VALUES = {}

class BadReference(Exception):
    pass

class InvalidReference(BadReference):
    pass

def dataset(name):
    if not name in DATASETS:
        DATASETS[name] = NKDataset(name, api_key=app.config['NOMENKLATURA_API_KEY'])
    return DATASETS[name]

def resolve(dataset_name, key):
    if (dataset_name, key) not in VALUES:
        resolver = dataset(dataset_name)
        try:
            obj = resolver.lookup(key)
        except NKInvalid, inv:
            obj = inv
        except NKNoMatch, nm:
            obj = nm
        VALUES[(dataset_name, key)] = obj
    obj = VALUES[(dataset_name, key)]
    if isinstance(obj, NKInvalid):
        raise InvalidReference()
    if isinstance(obj, NKNoMatch):
        raise BadReference()
    return obj.value

def resolve_type(key):
    return resolve(app.config['NOMENKLATURA_TYPES_DATASET'], key)

def resolve_person(key):
    return resolve(app.config['NOMENKLATURA_PERSONS_DATASET'], key)




