from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from app import db, login, app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(64))
    lastName = db.Column(db.String(64))
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    urole = db.Column(db.String(80))
    confirmed = db.Column(db.Boolean, nullable=False, default=False)
    confirmed_on = db.Column(db.DateTime, nullable=True)

    def __init__(self, email,firstName, lastName, urole, confirmed=False, admin=False, confirmed_on=None ):
        self.email = email
        self.firstName = firstName
        self.lastName = lastName
        self.urole = urole
        self.admin = admin
        self.confirmed = confirmed
        self.confirmed_on = confirmed_on

    def __repr__(self):
        return '<User {}>'.format(self.firstName)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def reset_token(self, expiryTime = 600):
        s = Serializer(app.config['SECRET_KEY'], expiryTime)
        return s.dumps({'user_id': self.id}).decode('utf-8')
    
    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(255), index=True, unique=True)
    score = db.Column(db.Float)

    #type = db.Column(db.String(16), index=True, unique=True)

class Option(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    qnId = db.Column(db.Integer)
    option = db.Column(db.String(255))

class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    optId = db.Column(db.Integer)
    userID = db.Column(db.Integer)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))