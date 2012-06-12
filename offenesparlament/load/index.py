import sys, re
import logging
from pprint import pprint
from datetime import datetime
from dateutil import tz
from sqlalchemy.orm import eagerload_all

from offenesparlament.core import db, solr
from offenesparlament.model import Gremium, NewsItem, Person, Rolle, \
        Wahlkreis, obleute, mitglieder, stellvertreter, Ablauf, \
        Position, Beschluss, Beitrag, Zuweisung, Referenz, Dokument, \
        Schlagwort, Sitzung, Debatte, Zitat

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

def strip_control_characters(text):
    if not isinstance(text, basestring):
        return text
    _filtered = []
    from unicodedata import category
    for c in unicode(text):
        cat = category(c)[:1]
        if cat not in 'C':
            _filtered.append(c)
    return ''.join(_filtered)
    #.encode('ascii', 'ignore')

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

def convert_text(data):
    for k, v in data.items():
        if isinstance(v, (list, tuple, set)):
            _v = []
            for e in v:
                e = strip_control_characters(e)
                _v.append(e)
            data[k] = _v
        else:
            data[k] = strip_control_characters(v)
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
    datas = []
    for position in Position.query.yield_per(1000):
        log.info("indexing %s - %s..." % (
            position.ablauf.titel, position.fundstelle))
        data = flatten(position.to_dict())
        data.update(type_info(position))
        data = convert_dates(data)
        datas.append(data)
        if len(datas) % 1000 == 0:
            sys.stdout.write(".")
            sys.stdout.flush()
            _solr.add_many(datas)
            _solr.commit()
            datas = []
    _solr.commit()

def index_dokumente():
    _solr = solr()
    datas = []
    for dokument in Dokument.query.yield_per(1000):
        log.info("indexing %s..." % dokument.name)
        data = flatten(dokument.to_dict())
        data.update(type_info(dokument))
        data = convert_dates(data)
        datas.append(data)
        if len(datas) % 1000 == 0:
            sys.stdout.write(".")
            sys.stdout.flush()
            _solr.add_many(datas)
            _solr.commit()
            datas = []
    _solr.commit()

def index_ablaeufe():
    _solr = solr()
    datas = []
    for ablauf in Ablauf.query.yield_per(1000):
        log.info("indexing %s..." % ablauf.titel)
        data = ablauf.to_dict()
        data['positionen'] = [p.to_dict() for p in \
                ablauf.positionen]
        data['positionen'] = [p.to_dict() for p in ablauf.positionen]
        dates = [p['date'] for p in data['positionen'] if p['date'] is not None]
        if len(dates):
            data['date'] = max(dates)
        data = flatten(data)
        data.update(type_info(ablauf))
        data = convert_dates(data)
        datas.append(data)
        if len(datas) % 500 == 0:
            sys.stdout.write(".")
            sys.stdout.flush()
            _solr.add_many(datas)
            _solr.commit()
            datas = []
    _solr.commit()


def index_sitzungen():
    _solr = solr()
    datas = []
    for sitzung in Sitzung.query:
        log.info("indexing %s..." % sitzung.titel)
        data = sitzung.to_dict()
        #data['zitate'] = [z.to_dict() for z in sitzung.zitate]
        data = flatten(data)
        data.update(type_info(sitzung))
        data = convert_dates(data)
        data = convert_text(data)
        datas.append(data)
        if len(datas) % 5 == 0:
            _solr.add_many(datas)
            datas = []
    _solr.add_many(datas)
    _solr.commit()

def index_debatten():
    _solr = solr()
    datas = []
    for debatte in Debatte.query:
        log.info("indexing %s..." % debatte.titel)
        data = debatte.to_dict()
        #data['zitate'] = [dz.zitat.to_dict() for dz in \
        #    debatte.debatten_zitate]
        data['sitzung'] = debatte.sitzung.to_dict()
        data = flatten(data)
        data.update(type_info(debatte))
        data = convert_dates(data)
        data = convert_text(data)
        datas.append(data)
        if len(datas) % 20 == 0:
            _solr.add_many(datas)
            datas = []
    _solr.add_many(datas)
    _solr.commit()

def index_zitate():
    _solr = solr()
    log.info("indexing transcripts...")
    datas = []
    for zitat in Zitat.query.yield_per(5000):
        data = zitat.to_dict()
        data['sitzung'] = zitat.sitzung.to_dict()
        data['debatte'] = zitat.debatte.to_dict()
        data = flatten(data)
        data.update(type_info(zitat))
        data = convert_dates(data)
        data = convert_text(data)
        data['date'] = data.get('sitzung.date')
        datas.append(data)
        if len(datas) % 1000 == 0:
            sys.stdout.write(".")
            sys.stdout.flush()
            _solr.add_many(datas)
            _solr.commit()
            datas = []
    _solr.add_many(datas)
    _solr.commit()

def index():
    _solr = solr()
    #_solr.delete_query("*:*")
    index_persons()
    index_gremien()
    index_positionen()
    index_dokumente()
    index_ablaeufe()
    index_sitzungen()
    index_debatten()
    index_zitate()

if __name__ == '__main__':
    #gather_index_fields()
    index()
    #index_debatten()
