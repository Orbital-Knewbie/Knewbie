import os
import unittest

from flask import url_for
from flask_login import current_user, login_user, logout_user, login_required
from app import create_app, db, mail, login
from app.models import *
from config import TestingConfig

from datetime import datetime

basedir = os.path.abspath(os.path.dirname(__file__))
 
 
TEST_DB = 'test.db'
 
 
class BaseTest(unittest.TestCase):
 
    ############################
    #### setup and teardown ####
    ############################
 
    # executed prior to each test
    def setUp(self):
        app = create_app(TestingConfig)
        self.app = app.test_client()

        ## IMPORTANT FOR LOGIN ##
        app.test_request_context().push()

        db.session.remove()
        db.drop_all()
        db.create_all()
        self.add_admin()
        self.add_test_forum()
        self.add_test_quiz_edu()
        self.add_test_question()

        # Disable sending emails during unit testing
        mail.init_app(app)
        self.assertEqual(app.debug, False)
 
    # executed after each test
    def tearDown(self):
        pass
    
    ########################
    #### helper methods ####
    ########################
    def register(self, role, *rdata):
        fields=('firstName', 'lastName', 'email', 'password', 'password2')
        pre = role[:3] + '-'
        data = {}
        for i in range(len(fields)):
            data[pre+fields[i]] = rdata[i]
        return self.app.post(
            url_for('auth.reg') + '/' + role,
            data=data,
            follow_redirects=True
        )
 
    def register_student(self, *data):
        return self.register('student', *data)

    def register_educator(self, *data):
        return self.register('educator', *data)
        
 
    def login(self, email, password):

        return self.app.post(
            url_for('auth.login'),
            data={'email' : email, 'password' : password },
            follow_redirects=True
        )
 
    def logout(self):
        return self.app.get(
            url_for('auth.logout'),
            follow_redirects=True
        )

    def add_admin(self):
        user = User(admin=True)
        db.session.add(user)


    def add_test_user(self):
        u = User(firstName="first", lastName="last", email="testes@test.com", \
            urole="student", knewbie_id="123456", curr_theta=-1.33, confirmed=True)
        u.set_password("test")
        return u

    def add_test_edu(self):
        u = User(firstName="yo", lastName="lo", email="edutest@test.com", \
            urole="educator", confirmed=True)
        u.set_password("strongtest")
        return u

    def add_test_group(self, name):
        return Group(name=name, classCode='654321')

    def add_test_thread(self, group, title):
        return Thread(group=group,timestamp=datetime.now(), title=title)

    def add_test_post(self, user, thread, content):
        return Post(user=user, thread=thread, 
                timestamp=datetime.now(), content=content)

    def add_test_quiz(self, user):
        return Quiz(userID=user.id,name="testquiz")

    def add_test_option(self, text):
        return Option(qnID=1, option=text)

    def add_test_options(self):
        lst = []
        for i in range(4):
            o = self.add_test_option('testoption' + str(i))
            lst.append(o)
        return lst

    def add_test_qn(self):
        return Question(userID=1,question='testquestion', discrimination=0, \
            difficulty=0,  guessing=0, upper=0, topicID = 1, answerID = 1)
    
    def add_test_topic(self):
        return Topic(name="General")

    def add_test_question(self):
        q = self.add_test_qn()
        opts = self.add_test_options()
        db.session.add(q)
        for o in opts:
            db.session.add(o)
        db.session.commit()

    def add_test_forum(self):
        u = self.add_test_user()
        e = self.add_test_edu()
        g = self.add_test_group("name")
        t = self.add_test_thread(g, "first thread")
        p = self.add_test_post(u, t, "first post")
        g.users.append(u)
        g.users.append(e)
        db.session.add(p)
        db.session.commit()

    def add_test_quiz_edu(self):
        t = self.add_test_topic()
        u = User.query.filter_by(urole='educator').first()
        q = self.add_test_quiz(u)
        qn = self.add_test_qn()
        q.questions.append(qn)
        db.session.add(q)
        db.session.commit()


    # Test Code from app.questions

    #def add_test_topics(self):
    #    remove_topics()
    #    if Topic.query.all(): return
    #    topics = ('General', 'Estimation', 'Geometry', 'Model')
    #    for topic in topics:
    #        add_topic(topic)

    #def test_insert_qns(self):
    #    '''To test insert_qns() works'''
    #    insert_qns('app/static/resources/questions')
    #    questions = Question.query.all()
    #    for q in questions:
    #        options = Option.query.filter_by(qnID=q.id)
    #        answer = q.answerID
    #        print(q.question)
    #        for o in options:
    #            if o.id == answer:
    #                ans_opt = o
    #            print(o.option)

    #        print("ANS" + o.option)
