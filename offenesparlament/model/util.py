import uuid
from datetime import datetime

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

