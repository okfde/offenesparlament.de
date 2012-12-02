from datetime import datetime

from offenesparlament.core import db


class Zuweisung(db.Model):
    __tablename__ = 'zuweisung'

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Unicode())
    federfuehrung = db.Column(db.Boolean())

    gremium_id = db.Column(db.Integer, db.ForeignKey('gremium.id'))
    position_id = db.Column(db.Integer, db.ForeignKey('position.id'))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow)

    def to_ref(self):
        return {
                'id': self.id,
                'text': self.text,
                'federfuehrung': self.federfuehrung,
                'gremium': self.gremium.key if self.gremium else None,
                'position': self.position.id if self.position else None
                }

    def to_dict(self):
        data = self.to_ref()
        data.update({
            'gremium': self.gremium.to_ref(),
            'position': self.position.to_ref(),
            'created_at': self.created_at,
            'updated_at': self.updated_at
            })
        return data

