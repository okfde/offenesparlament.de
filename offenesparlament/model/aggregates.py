from datetime import datetime

from offenesparlament.core import db


current_schlagwort = db.Table('current_schlagwort', db.metadata,
        db.Column('schlagwort', db.Unicode),
        db.Column('num', db.Integer),
        db.Column('period', db.Unicode))

period_sachgebiet = db.Table('period_sachgebiet', db.metadata,
        db.Column('sachgebiet', db.Unicode),
        db.Column('num', db.Integer),
        db.Column('period', db.Unicode))

person_schlagwort = db.Table('person_schlagwort', db.metadata,
        db.Column('person_id', db.Integer),
        db.Column('schlagwort', db.Unicode),
        db.Column('num', db.Integer))

