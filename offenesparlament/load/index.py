import sys
import logging
from pprint import pprint
from datetime import datetime
from dateutil import tz

from offenesparlament.core import db, solr
from offenesparlament.model import Gremium, NewsItem, Person, Rolle, \
        Wahlkreis, obleute, mitglieder, stellvertreter, Ablauf, \
        Position, Beschluss, Beitrag, Zuweisung, Referenz, Dokument, \
        Schlagwort

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.NOTSET)

def datetime_add_tz(dt):
    """ Solr requires time zone information on all dates. """
    return datetime(dt.year, dt.month, dt.day, dt.hour,
                    dt.minute, dt.second, tzinfo=tz.tzutc())

def flatten(data, sep='.'):
    _data = {}
    for k, v in data.items():
        if isinstance(v, dict):
            for ik, iv in flatten(v, sep=sep).items():
                _data[k + sep + ik] = iv
        elif isinstance(v, (list, tuple)):
            for iv in v:
                if isinstance(iv, dict):
                    for lk, lv in flatten(iv, sep=sep).items():
                        key = k + sep + lk
                        if key in _data:
                            if not isinstance(_data[key], set):
                                _data[key] = set([_data[key]])
                            _data[key].add(lv)
                        else:
                            _data[key] = lv
                else:
                    _data[k] = v
                    break
        else:
            _data[k] = v
    return _data


def gather_index_fields():
    from collections import defaultdict
    fields = defaultdict(set)
    for _type in [Person, Gremium, Position, Dokument]:
        print _type.__name__
        for entity in _type.query:
            d = flatten(entity.to_dict())
            for k, v in d.items():
                fields[k].add(type(v))
    for entity in Ablauf.query:
        data = entity.to_dict()
        data['positionen'] = [p.to_dict() for p in \
                entity.positionen]
        d = flatten(data)
        for k, v in d.items():
            fields[k].add(type(v))
    pprint(dict([(f, [t for t in v if t is not type(None)]) \
            for (f, v) in fields.items()]))

def type_info(entity):
    name = entity.__class__.__name__.lower()
    return {
            'index_type': name, 
            'typed_id': "%s:%s" % (name, entity.id)
            }

def convert_dates(data):
    for k, v in data.items():
        if isinstance(v, datetime):
            data[k] = datetime_add_tz(v)
        elif isinstance(v, (list, tuple, set)):
            _v = []
            for e in v:
                if isinstance(e, datetime):
                    e = datetime_add_tz(e)
                _v.append(e)
            data[k] = _v
    return data

def index_persons():
    _solr = solr()
    for person in Person.query:
        log.info("indexing %s..." % person.name)
        data = flatten(person.to_dict())
        data.update(type_info(person))
        data = convert_dates(data)
        _solr.add_many([data])
    _solr.commit()

def index_gremien():
    _solr = solr()
    for gremium in Gremium.query:
        log.info("indexing %s..." % gremium.name)
        data = flatten(gremium.to_dict())
        data.update(type_info(gremium))
        data = convert_dates(data)
        _solr.add_many([data])
    _solr.commit()

def index_positionen():
    _solr = solr()
    for position in Position.query:
        log.info("indexing %s - %s..." % (
            position.ablauf.titel, position.fundstelle))
        data = flatten(position.to_dict())
        data.update(type_info(position))
        data = convert_dates(data)
        _solr.add_many([data])
    _solr.commit()

def index_dokumente():
    _solr = solr()
    for dokument in Dokument.query:
        log.info("indexing %s..." % dokument.name)
        data = flatten(dokument.to_dict())
        data.update(type_info(dokument))
        data = convert_dates(data)
        _solr.add_many([data])
    _solr.commit()

def index_ablaeufe():
    _solr = solr()
    for ablauf in Ablauf.query:
        log.info("indexing %s..." % ablauf.titel)
        data = ablauf.to_dict()
        data['positionen'] = [p.to_dict() for p in \
                ablauf.positionen]
        data = flatten(data)
        data.update(type_info(ablauf))
        data = convert_dates(data)
        _solr.add_many([data])
    _solr.commit()

def index():
    #index_persons()
    #index_gremien()
    index_positionen()
    index_dokumente()
    index_ablaeufe()



if __name__ == '__main__':
    #gather_index_fields()
    index()

