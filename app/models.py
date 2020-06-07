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
    admin = db.Column(db.Boolean, nullable=False, default=False)
    theta = db.Column(db.Float)

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

    def get_AI_responses(self):
        '''Method to retrive Administered Items (AI) and response vector'''

        # Retrieve stored responses from DB
        responses = Response.query.filter_by(userID=self.id).all()
        # Get AI / qnID from Responses
        AI = [x.qnID for x in responses]

        # Compare all responses with correct answer and store in resp_vector - in order
        resp_vector = []
        for qn in AI:
            ans = Answer.query.filter_by(qnID=qn).first()
            resp = Response.query.filter_by(userID=self.id,qnID=qn).first()
            resp_vector.append(ans.optID==resp.optID)

        return AI, resp_vector


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(255), index=True, unique=True)
    discrimination = db.Column(db.Float)
    difficulty = db.Column(db.Float)
    guessing = db.Column(db.Float)
    upper = db.Column(db.Float)

    #type = db.Column(db.String(16), index=True, unique=True)

class Option(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    qnID = db.Column(db.Integer)
    option = db.Column(db.String(255))

class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    optID = db.Column(db.Integer)
    qnID = db.Column(db.Integer)

class Response(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userID = db.Column(db.Integer)
    optID = db.Column(db.Integer)
    qnID = db.Column(db.Integer)

class UserClass(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    classID = db.Column(db.Integer)
    userID = db.Column(db.Integer)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userclassID = db.Column(db.Integer)
    title = db.Column(db.String(120))
    content = db.Column(db.String(140))

@login.user_loader
def load_user(id):
    return User.query.get(int(id))