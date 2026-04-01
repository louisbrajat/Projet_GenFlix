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
    idtvmaze = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), unique=True, nullable=False)
    img = db.Column(db.String())
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    user = db.relationship("User", backref="serie")
    



