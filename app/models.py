from werkzeug.security import generate_password_hash, check_password_hash
from hashlib import md5
from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from time import time
import jwt
import sqlalchemy as sa

from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()


from app import db, login
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from hashlib import md5

db = SQLAlchemy()

from app import db, login

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)

    def avatar(self, size):
        """Generate a Gravatar URL for the user's avatar."""
        digest = md5(self.username.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'

    def __repr__(self):
        return f'<User {self.username}>'

@login.user_loader
def load_user(user_id):
    """Flask-Login user loader callback."""
    return User.query.get(int(user_id))