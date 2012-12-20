import sys, re
import logging
from pprint import pprint
from datetime import datetime
from dateutil import tz
from sqlalchemy.orm import eagerload_all
from unicodedata import category

from offenesparlament.core import db, solr
from offenesparlament.model import Gremium, NewsItem, Person, Rolle, \
        Wahlkreis, Ablauf, \
        Position, Beschluss, Beitrag, Zuweisung, Referenz, Dokument, \
        Schlagwort, Sitzung, Debatte, Zitat

log = logging.getLogger(__name__)

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
                            if isinstance(lv, set):
                                _data[key].union(lv)
                            else:
                                _data[key].add(lv)
                        else:
                            _data[key] = lv
                else:
                    _data[k] = v
                    break
        else:
            _data[k] = v
    return _data

def strip_control_characters(text):
    """ For text strings, remove control characters as they may cause 
    the indexer to stumble. """
    if not isinstance(text, basestring):
        return text
    _filtered = []
    for c in unicode(text):
        cat = category(c)[:1]
        if cat not in 'C':
            _filtered.append(c)
    return ''.join(_filtered)

def convert_data(data):
    for k, v in data.items():
        if isinstance(v, datetime):
            data[k] = datetime_add_tz(v)
        elif isinstance(v, (list, tuple, set)):
            _v = []
            for e in v:
                if isinstance(e, datetime):
                    e = datetime_add_tz(e)
                else:
                    e = strip_control_characters(e)
                _v.append(e)
            data[k] = _v
        else:
            data[k] = strip_control_characters(v)
    return data

def index_class(cls, step=1000):
    _solr = solr()
    entities = []
    log.info("Indexing %s", cls.__name__)
    for obj in cls.query.yield_per(step):
        entity = obj.to_index()
        entity = convert_data(flatten(entity))
        entities.append(entity)
        if len(entities) % step == 0:
            sys.stdout.write(".")
            sys.stdout.flush()
            _solr.add_many(entities)
            _solr.commit()
            entities = []
    if len(entities):
        _solr.add_many(entities)
    _solr.commit()


def index():
    _solr = solr()
    #_solr.delete_query("*:*")
    index_class(Person)
    #index_class(Gremium)
    #index_class(Position)
    #index_class(Dokument)
    index_class(Ablauf)
    index_class(Sitzung)
    index_class(Debatte)
    index_class(Zitat)

if __name__ == '__main__':
    index()
