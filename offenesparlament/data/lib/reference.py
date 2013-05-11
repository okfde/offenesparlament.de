import logging
from threading import Lock

from nomenklatura import Dataset, Entity

from offenesparlament.core import app

log = logging.getLogger(__name__)

DATASETS = {}
ENTITIES = {}
LOCK = Lock()

class BadReference(Exception):
    pass

class InvalidReference(BadReference):
    pass

def dataset(name):
    if not name in DATASETS:
        DATASETS[name] = Dataset(name, api_key=app.config['NOMENKLATURA_API_KEY'])
        if app.config['NOMENKLATURA_PRELOAD']:
            for entity in DATASETS[name].entities():
                ENTITIES[(name, entity.name.lower())] = entity
            for alias in DATASETS[name].aliases():
                if alias.is_invalid:
                    ENTITIES[(name, alias.name.lower())] = \
                        Dataset.Invalid({'dataset': alias.dataset, 'name': alias.name})
                elif alias.is_matched:
                    ENTITIES[(name, alias.name.lower())] = \
                        Entity(DATASETS[name], alias.entity)
    return DATASETS[name]

def resolve(dataset_name, key):
    LOCK.acquire()
    try:
        cache_tpl = (dataset_name, key.lower())
        if cache_tpl not in ENTITIES:
            resolver = dataset(dataset_name)
            try:
                obj = resolver.lookup(key)
            except Dataset.Invalid, inv:
                obj = inv
            except Dataset.NoMatch, nm:
                obj = nm
            ENTITIES[cache_tpl] = obj
        obj = ENTITIES[cache_tpl]
        if isinstance(obj, Dataset.Invalid):
            raise InvalidReference()
        if isinstance(obj, Dataset.NoMatch):
            raise BadReference()
        return obj.name
    finally:
        LOCK.release()

def resolve_type(key):
    return resolve(app.config['NOMENKLATURA_TYPES_DATASET'], key)

def resolve_person(key):
    return resolve(app.config['NOMENKLATURA_PERSONS_DATASET'], key)

def resolve_votes(key):
    return resolve(app.config['NOMENKLATURA_VOTES_DATASET'], key)

def resolve_stage(key):
    return resolve(app.config['NOMENKLATURA_STAGE_DATASET'], key)


