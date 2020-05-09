from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    urole = db.Column(db.String(80))

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(255), index=True, unique=True)
    score = db.Column(db.Float)

    #type = db.Column(db.String(16), index=True, unique=True)

class Option(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    qnId = db.Column(db.Integer)
    option = db.Column(db.String(255), index=True, unique=True)

class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    optId = db.Column(db.Integer)
    answer = db.Column(db.String(255), index=True, unique=True)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))