# tests/test_groups.py
 
 
import os
import unittest

from flask import url_for
from flask_login import current_user, login_user, logout_user, login_required
from app import app, db, mail, login
from app.models import *
from app.group import *
from app.forum import *

from datetime import datetime

basedir = os.path.abspath(os.path.dirname(__file__))
 
 
TEST_DB = 'test.db'
 
 
class BasicTests(unittest.TestCase):
 
    ############################
    #### setup and teardown ####
    ############################
 
    # executed prior to each test
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
            os.path.join(basedir, TEST_DB)
        app.testing = True
        self.app = app.test_client()

        ## IMPORTANT FOR LOGIN ##
        app.test_request_context().push()

        db.session.remove()
        db.drop_all()
        db.create_all()
        self.add_test_forum()
        self.add_test_edu()

        # Disable sending emails during unit testing
        mail.init_app(app)
        self.assertEqual(app.debug, False)
 
    # executed after each test
    def tearDown(self):
        pass
    
    ########################
    #### helper methods ####
    ########################
    def login(self, email, password):
        return self.app.post(
            '/login',
            data={'email' : email, 'password' : password },
            follow_redirects=True
        )

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
        return Group(name=name)

    def add_test_thread(self, group, title):
        return Thread(group=group,timestamp=datetime.now(), title=title)

    def add_test_post(self, user, thread, content):
        return Post(user=user, thread=thread, 
                timestamp=datetime.now(), content=content)

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

    ###############
    #### tests ####
    ###############
    def test_basic_group(self):
        '''Basic access to class sites'''
        with self.app:
            self.login('testes@test.com', 'test')
            pages = ('leaderboard', 'forum', 'create_thread')
            for page in pages:
                rv = self.app.get(url_for(page,groupID=1))
                self.assertEqual(rv.status_code, 200)

    def test_edu_group(self):
        '''Basic educator-only access to class sites'''
        with self.app:
            self.login('edutest@test.com', 'strongtest')
            pages = ('createclasssuccess', 'delete_class', 'edit_participants')
            for page in pages:
                rv = self.app.get(url_for(page,groupID=1))
                self.assertEqual(rv.status_code, 200)
    
    def test_restrict_access(self):
        '''Restrict student from accessing educator class sites'''
        with self.app:
            self.login('testes@test.com', 'test')
            pages = ('createclasssuccess', 'delete_class', 'edit_participants')
            for page in pages:
                rv = self.app.get(url_for(page,groupID=1))
                self.assertEqual(rv.status_code, 403)

    def test_edu_group(self):
        '''POST only sites'''
        with self.app:
            self.login('edutest@test.com', 'strongtest')
            
            rv = self.app.get(url_for('adduserclass',groupID=1))
            self.assertEqual(rv.status_code, 405)

            rv = self.app.get(url_for('delete_participant',groupID=1,userID=1))
            self.assertEqual(rv.status_code, 405)

    def test_forum_thread(self):
        '''Forum thread access'''
        with self.app:
            self.login('edutest@test.com', 'strongtest')

            rv = self.app.get(url_for('forum_post',groupID=1, threadID=1))
            self.assertEqual(rv.status_code, 200)

            rv = self.app.get(url_for('edit_post',groupID=1, threadID=1, postID=1))
            self.assertEqual(rv.status_code, 200)

    def test_post_thread(self):
        '''Forum POST only'''
        with self.app:
            self.login('edutest@test.com', 'strongtest')

            rv = self.app.get(url_for('delete_thread',groupID=1, threadID=1, postID=1))
            self.assertEqual(rv.status_code, 405)

            rv = self.app.get(url_for('delete_post',groupID=1, threadID=1, postID=1))
            self.assertEqual(rv.status_code, 405)

 
if __name__ == "__main__":
    unittest.main()