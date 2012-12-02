from offenesparlament.core import db

schlagworte = db.Table('schlagworte',
    db.Column('schlagwort_id', db.Integer, db.ForeignKey('schlagwort.id')),
    db.Column('ablauf_id', db.Integer, db.ForeignKey('ablauf.id'))
)


class Schlagwort(db.Model):
    __tablename__ = 'schlagwort'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode())

