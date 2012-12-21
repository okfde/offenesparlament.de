import uuid
from datetime import datetime
from dateutil import tz

from offenesparlament.core import db


class ModelCore(object):
    id = db.Column(db.Integer, primary_key=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow)

    def _type_info(self):
        t = self.__class__.__name__.lower()
        return {
                'index_type': t,
                'typed_id': '%s:%s' % (t, self.id)
                }

    def to_index(self):
        data = self.to_dict()
        data.update(self._type_info())
        return data


def make_token():
    return uuid.uuid4().get_hex()[15:]


def datetime_add_tz(dt):
    """ Solr requires time zone information on all dates. """
    return datetime(dt.year, dt.month, dt.day, dt.hour,
                    dt.minute, dt.second, tzinfo=tz.tzutc())


def to_date(text):
    try:
        return datetime.strptime(text, "%Y-%m-%dT%H:%M:%S")
    except:
        pass


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


def convert_data_to_index(data):
    from offenesparlament.data.lib.text import strip_control_characters
    for k, v in flatten(data).items():
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


