from datetime import datetime

from offenesparlament.core import db
from offenesparlament.model.util import ModelCore


class Beschluss(db.Model, ModelCore):
    __tablename__ = 'beschluss'

    dokument_text = db.Column(db.Unicode())
    tenor = db.Column(db.Unicode())
    seite = db.Column(db.Unicode())

    position_id = db.Column(db.Integer, db.ForeignKey('position.id'))

    def to_ref(self):
        return {
                'id': self.id,
                'dokument_text': self.dokument_text,
                'tenor': self.tenor,
                'seite': self.seite,
                'position': self.position.id
                }

    def to_dict(self):
        data = self.to_ref()
        data.update({
            'dokument': self.dokument.to_ref(),
            'position': self.position.to_ref(),
            'created_at': self.created_at,
            'updated_at': self.updated_at
            })
        return data

