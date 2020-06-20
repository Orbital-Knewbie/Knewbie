import string
import random
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from app import db, login, app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

usergroup = db.Table('usergroup', \
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True), \
    db.Column('group_id', db.Integer, db.ForeignKey('group.id'), primary_key=True)
)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(64))
    lastName = db.Column(db.String(64))
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    urole = db.Column(db.String(80))
    confirmed = db.Column(db.Boolean, nullable=False, default=False)
    confirmed_on = db.Column(db.DateTime, nullable=True)
    knewbie_id = db.Column(db.String(8), nullable=True, unique=True)
    image_file = db.Column(db.String(20), default='profileimg.jpg')
    admin = db.Column(db.Boolean, nullable=False, default=False)
    curr_theta = db.Column(db.Float)
    groups = db.relationship('Group', secondary=usergroup, backref='users')
    posts = db.relationship('Post', backref='user')
    responses = db.relationship('Response')
    proficiencies = db.relationship('Proficiency')
    quizzes = db.relationship('Quiz')

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

    def set_knewbie_id(self):
        lettersAndDigits = string.ascii_letters + string.digits
        self.knewbie_id =  ''.join((random.choice(lettersAndDigits) for i in range(8)))
        return self.knewbie_id

questionquiz = db.Table('questionquiz', \
    db.Column('question_id', db.Integer, db.ForeignKey('question.id'), primary_key=True), \
    db.Column('quiz_id', db.Integer, db.ForeignKey('quiz.id'), primary_key=True)
)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(255), index=True, unique=True)
    discrimination = db.Column(db.Float)
    difficulty = db.Column(db.Float)
    guessing = db.Column(db.Float)
    upper = db.Column(db.Float)
    topicID = db.Column(db.Integer, db.ForeignKey('topic.id'))
    topic = db.relationship('Topic', backref='questions')
    options = db.relationship('Option')
    answerID = db.Column(db.Integer, db.ForeignKey('answer.id'))
    answer = db.relationship('Answer', backref=db.backref('question', uselist=False))
    responses = db.relationship('Response')


    #type = db.Column(db.String(16), index=True, unique=True)

class Option(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    qnID = db.Column(db.Integer, db.ForeignKey('question.id'))
    option = db.Column(db.String(255))
    responses = db.relationship('Response')
    answer = db.relationship('Answer', backref=db.backref('option', uselist=False))
    answerID = db.Column(db.Integer, db.ForeignKey('answer.id'))

class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)

class Response(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userID = db.Column(db.Integer, db.ForeignKey('user.id'))
    optID = db.Column(db.Integer, db.ForeignKey('option.id'))
    qnID = db.Column(db.Integer, db.ForeignKey('question.id'))




class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    threads = db.relationship('Thread', backref='group')


class Thread(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime)
    title = db.Column(db.String(120))
    posts = db.relationship('Post', backref='thread')
    groupID = db.Column(db.Integer, db.ForeignKey('group.id'))


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime)
    content = db.Column(db.Text)
    threadID = db.Column(db.Integer, db.ForeignKey('thread.id'))
    userID = db.Column(db.Integer, db.ForeignKey('user.id'))

class Proficiency(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userID = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.DateTime)
    theta = db.Column(db.Float)
    topicID = db.Column(db.Integer, db.ForeignKey('topic.id'))

    def get_AI_responses(self):
        '''Method to retrive Administered Items (AI) and response vector'''

        # Retrieve stored responses from DB
        responses = Response.query.filter_by(userID=self.userID).all()

        # Get AI / qnID from Responses
        if self.topicID == 1 or self.topicID is None:
            AI = [resp.qnID - 1 for resp in responses]
        else:
            # Get relevant topic questions
            questions = Question.query.filter_by(topicID=self.topicID).all()
            questions = {qn.id for qn in questions}
            AI = []
            for resp in responses:
                if resp.qnID in questions:
                    AI.append(resp.qnID - 1)

        # Compare all responses with correct answer and store in resp_vector - in order
        resp_vector = []
        for qn in AI:
            ans = Answer.query.filter_by(qnID=qn+1).first()
            resp = Response.query.filter_by(userID=self.userID,qnID=qn+1).first()

            resp_vector.append(ans.optID==resp.optID)

        return AI, resp_vector

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userID = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String(120))
    questions = db.relationship('Question', secondary=questionquiz, backref='quizzes')

class Topic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    proficiencies = db.relationship('Proficiency')

@login.user_loader
def load_user(id):
    return User.query.get(int(id))