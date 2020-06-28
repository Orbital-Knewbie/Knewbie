# tests/test_groups.py
 
 
import os
import unittest

from flask import url_for
from flask_login import current_user, login_user, logout_user, login_required
from app import app, db, mail, login
from app.models import *
from app.group import *
from app.forum import *
from app.tests.basetest import BaseTest

from datetime import datetime

basedir = os.path.abspath(os.path.dirname(__file__))
 
 
TEST_DB = 'test.db'
 
 
class BasicTests(BaseTest):

    ###############
    #### tests ####
    ###############
    def test_basic_group(self):
        '''Basic access to class sites'''
        with self.app:
            self.login('testes@test.com', 'test')
            pages = ('leaderboard', 'forum', 'create_thread', 'classquiz')
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

    def test_edu_post(self):
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
            
            rv = self.app.get(url_for('joinclass'))
            self.assertEqual(rv.status_code, 405)            
            
            rv = self.app.get(url_for('createclass'))
            self.assertEqual(rv.status_code, 405)

    def test_join_class(self):
        '''Student join class with code'''
        with self.app:
            self.login('testes@test.com', 'test')
            rv = self.app.post(url_for('joinclass'), data={'join-title': '654321'}, follow_redirects=True)
            self.assertEqual(rv.status_code, 200)
            self.assertIn(b'654321', rv.data)
            self.assertIn(b'Create A New Thread', rv.data)

    def test_create_class(self):
        '''Educator create class'''
        with self.app:
            self.login('edutest@test.com', 'strongtest')
            rv = self.app.post(url_for('createclass'), data={'class-title':'test class'}, follow_redirects=True)
            self.assertEqual(rv.status_code, 200)
            self.assertIn(b'Class was successfully created!', rv.data)
            self.assertIn(b'Please share the class code with only the parties you want to add to the class.', rv.data)

    def test_create_dup_class(self):
        '''Educator create class same name'''
        with self.app:
            self.login('edutest@test.com', 'strongtest')
            rv = self.app.post(url_for('createclass'), data={'class-title':'name'}, follow_redirects=True)
            self.assertEqual(rv.status_code, 200)
            self.assertIn(b'You have already created a Class with this name. Please choose a different name.', rv.data)


    def test_delete_class(self):
        '''Educator delete class'''
        with self.app:
            self.login('edutest@test.com', 'strongtest')
            rv = self.app.post(url_for('delete_class', groupID=1), data={'title': '654321'}, follow_redirects=True)
            self.assertEqual(rv.status_code, 200)
            self.assertIn(b'Class deleted', rv.data)
            self.assertIn(b'View Your Classes', rv.data)


    def test_add_userclass(self):
        '''Educator adds student and duplicate student to class'''
        with self.app:
            self.login('edutest@test.com', 'strongtest')
            u = User(knewbie_id='test12')
            db.session.add(u)
            db.session.commit()
            rv = self.app.post(url_for('adduserclass', groupID=1), data={'title': 'test12'}, follow_redirects=True)
            self.assertEqual(rv.status_code, 200)
            self.assertIn(b'User added', rv.data)
            self.assertIn(b'Edit Participants', rv.data)
            rv = self.app.post(url_for('adduserclass', groupID=1), data={'title': '123456'}, follow_redirects=True)
            self.assertEqual(rv.status_code, 200)
            self.assertIn(b'User already in Class', rv.data)
 
    def test_delete_userclass(self):
        '''Educator deletes user from class'''
        with self.app:
            self.login('edutest@test.com', 'strongtest')
            u = User.query.filter_by(knewbie_id='123456').filter(User.groups.any(id=1)).first()
            self.assertIsNotNone(u)
            rv = self.app.post(url_for('delete_participant', groupID=1, userID=u.id), data={}, follow_redirects=True)
            self.assertEqual(rv.status_code, 200)
            self.assertIn(b'User deleted', rv.data)
            self.assertIn(b'Edit Participants', rv.data)
            
            u2 = User.query.filter_by(id=u.id).filter(User.groups.any(id=1)).first()
            self.assertIsNone(u2)


if __name__ == "__main__":
    unittest.main()