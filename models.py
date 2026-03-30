import hashlib
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
db = SQLAlchemy()
sess = Session()
import secrets

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Pseudo = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    Email = db.Column(db.String(80), nullable=False)

    
    @classmethod
    def get_by_username(cls, username):
        return cls.query.filter_by(username=username).first()


class ApiKey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(100), nullable=False)
    key_hash = db.Column(db.String(255), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    user = db.relationship("User", backref="api_keys")