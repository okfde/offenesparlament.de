from datetime import datetime

from offenesparlament.core import db
from offenesparlament.model.util import make_token


class Abo(db.Model):
    __tablename__ = 'abo'

    id = db.Column(db.Integer, primary_key=True)

    query = db.Column(db.Unicode())
    email = db.Column(db.Unicode())
    offset = db.Column(db.DateTime, default=datetime.utcnow)
    activation_code = db.Column(db.Unicode(), default=make_token)
    include_activity = db.Column(db.Boolean)
    include_speeches = db.Column(db.Boolean)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow)

