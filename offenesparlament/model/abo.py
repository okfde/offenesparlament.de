from datetime import datetime

from offenesparlament.core import db
from offenesparlament.model.util import make_token
from offenesparlament.model.util import ModelCore


class Abo(db.Model, ModelCore):
    __tablename__ = 'abo'

    query = db.Column(db.Unicode())
    email = db.Column(db.Unicode())
    offset = db.Column(db.DateTime, default=datetime.utcnow)
    activation_code = db.Column(db.Unicode(), default=make_token)
    include_activity = db.Column(db.Boolean)
    include_speeches = db.Column(db.Boolean)

