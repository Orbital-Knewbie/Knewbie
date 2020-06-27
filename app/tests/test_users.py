import unittest, os
from flask import url_for
from flask_login import current_user
from app import app, db, mail
from app.models import User, Post
from app.profile import register
from app.email import generate_confirmation_token

from app.tests.basetest import BaseTest

basedir = os.path.abspath(os.path.dirname(__file__))

TEST_DB = 'test.db'

class UserModelCase(BaseTest):
    

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

    def test_register_student(self):
        '''Registration and confirmation of student'''
        with self.app:
            # Register
            response = self.register_student('yolo', 'amirite','patkennedy79@gmail.com', 'FlaskIsAwesome', 'FlaskIsAwesome')
            self.assertEqual(response.status_code, 200)
            u = User.query.filter_by(email='patkennedy79@gmail.com').first()
            self.assertEqual(u.firstName, 'yolo')
            self.assertEqual(u.lastName, 'amirite')
            self.assertFalse(u.confirmed)

            self.login('patkennedy79@gmail.com', 'FlaskIsAwesome')
            token = generate_confirmation_token(u.email)

            # Confirm Token
            response2 = self.app.get('/confirm/' + token, follow_redirects=True)
            self.assertEqual(response2.status_code, 200)
            u = User.query.filter_by(email='patkennedy79@gmail.com').first()
            self.assertTrue(u.confirmed)
            self.assertIn(b'You have confirmed your account. Thanks!', response2.data)
            response3 = self.app.get('/confirm/' + token, follow_redirects=True)
            self.assertIn(b'Account already confirmed. Please login.', response3.data)
            response4 = self.app.get('/confirm/lol')
            self.assertEqual(response4.status_code, 404)

    def test_logout(self):
        '''Login / Logout'''
        with self.app:
            response = self.login('testes@test.com','test')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Join A Class', response.data)
            response2 = self.logout()
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Knowledge is Power. Even if you are a Noobie.', response2.data)
            response = self.login('edutest@test.com', 'strongtest')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Create A New Class', response.data)
            self.assertIn(b'Create A New Quiz', response.data)
            response2 = self.logout()
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Knowledge is Power. Even if you are a Noobie.', response2.data)

    def test_confirmed(self):
        '''Redirect to dashboard, confirmed'''
        with self.app:
            self.login('testes@test.com','test')
            response = self.app.get(url_for('unconfirmed'), follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Join A Class', response.data)
            response = self.app.get(url_for('resend'), follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Join A Class', response.data)
        


if __name__ == '__main__':
    unittest.main()
