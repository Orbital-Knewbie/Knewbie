import unittest, os
from flask import url_for
from flask_login import current_user
from app import db, mail
from app.models import User, Post
from app.auth.profile import register

from app.tests.basetest import BaseTest

basedir = os.path.abspath(os.path.dirname(__file__))

TEST_DB = 'test.db'

class UserCase(BaseTest):
    

    ###############
    #### tests ####
    ###############

    def test_password_hashing(self):
        u = User(firstName='ramana')
        u.set_password('ramanalovesfootball')
        self.assertFalse(u.check_password('ramanalovesmaplestory'))
        self.assertTrue(u.check_password('ramanalovesfootball'))

    def test_invalid_user_registration_different_passwords(self):
        response = self.register_student('yolo', 'amirite', 'patkennedy79@gmail.com', 'FlaskIsAwesome', 'FlaskIsNotAwesome')
        self.assertIn(b'Field must be equal to password.', response.data)

    def test_invalid_user_registration_duplicate_email(self):
        response = self.register_student('yolo', 'amirite','patkennedy79@gmail.com', 'FlaskIsAwesome', 'FlaskIsAwesome')
        self.assertEqual(response.status_code, 200)
        response = self.register_student('yolo', 'amirite','patkennedy79@gmail.com', 'FlaskIsReallyAwesome', 'FlaskIsReallyAwesome')
        self.assertIn(b'Please use a different email address.', response.data)
        response = self.register_educator('yolo', 'amirite','patkennedy79@gmail.com', 'FlaskIsReallyAwesome', 'FlaskIsReallyAwesome')
        self.assertIn(b'Please use a different email address.', response.data)

    

    def test_post_report(self):
        '''POST request to progress report'''
        rv = self.app.post(url_for('main.get_report'), data={'code-title' : '123456'}, follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Proficiency by Difficulty', rv.data)
        self.assertIn(b'Topical Proficiency', rv.data)

    def test_edu_report(self):
        '''Educator accessing their own report (None)'''
        with self.app:
            self.login('edutest@test.com','strongtest')
            rv = self.app.get(url_for('main.get_report'), follow_redirects=True)
            self.assertEqual(rv.status_code, 200)
            self.assertIn(b'View Your Classes', rv.data)

    def test_stu_report(self):
        '''Student accessing their own report'''
        with self.app:
            self.login('testes@test.com','testtest')
            rv = self.app.get(url_for('main.get_report'), follow_redirects=True)
            self.assertEqual(rv.status_code, 200)
            self.assertIn(b'Proficiency by Difficulty', rv.data)
            self.assertIn(b'Topical Proficiency', rv.data)




if __name__ == '__main__':
    unittest.main()
