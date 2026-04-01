import hashlib
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

import secrets

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Pseudo = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    Email = db.Column(db.String(80), nullable=False)

    @classmethod
    def get_by_username(cls, username):
        return cls.query.filter_by(Pseudo=username).first()

class Serie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    idtvmaze = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(), unique=True, nullable=False)
    note = db.Column(db.Integer())
    img = db.Column(db.String())
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    user = db.relationship("User", backref="serie")

    def to_dict(self):
        return {
            "serie_idtvmaze": self.idtvmaze,
        }

    @classmethod
    def get_All_Serie(cls,user_id):
        return cls.query.filter_by(user_id=user_id)
    



