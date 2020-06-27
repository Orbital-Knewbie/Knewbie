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