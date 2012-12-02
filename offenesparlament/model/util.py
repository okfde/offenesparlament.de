import uuid
from offenesparlament.core import db


def make_token():
    return uuid.uuid4().get_hex()[15:]

