import unittest
from app.tests.basetest import BaseTest
from app.models import *
from app.auth.email import generate_confirmation_token

from flask import url_for
from flask_login import current_user

class AuthTest(BaseTest):
    def test_deactivate(self):
        with self.app:
            self.login('testes@test.com','testtest')
            rv = self.app.post(url_for('auth.request_deactivate'), data={'email':'testes@test.com'}, follow_redirects=True)
            self.assertEqual(rv.status_code, 200)
            user = User.query.filter_by(email='testes@test.com').first()
            token = user.reset_token()
            rv = self.app.get(url_for('auth.deactivate_account', token=token), follow_redirects=True)
            self.assertEqual(rv.status_code, 200)
            self.assertIn(b'Your account has been successfully deactivated! Thank you.', rv.data)
            self.assertIn(b'Knowledge is Power. Even if you are a Noobie.', rv.data)
            user = User.query.filter_by(email='testes@test.com').first()
            self.assertIsNone(user)
    
    def test_settings(self):
        '''Settings page'''
        with self.app:
            self.login('testes@test.com','testtest')
            rv = self.app.get(url_for('main.settings'), follow_redirects=True)
            self.assertEqual(rv.status_code, 200)
            self.assertIn(b'New Password', rv.data)
            self.assertIn(b'Confirm Email', rv.data)
            self.assertIn(b'Danger Zone', rv.data)

    def test_update_profile(self):
        '''Update username'''
        with self.app:
            self.login('testes@test.com','testtest')
            rv = self.app.post(url_for('main.settings'), data={'profile-firstName':'newfirstname', 'profile-lastName':'newlastname'}, follow_redirects=True)
            self.assertEqual(rv.status_code, 200)
            self.assertEqual(current_user.firstName, 'newfirstname')
            self.assertEqual(current_user.lastName, 'newlastname')


    def test_reset_authenticated(self):
        with self.app:
            self.login('testes@test.com','testtest')
            rv = self.app.get(url_for('auth.request_reset_password'), follow_redirects=True)
            self.assertEqual(rv.status_code, 200)
            self.assertIn(b'View Your Classes', rv.data)

    def test_reset_password(self):
        '''Reset password'''
        with self.app:
            self.login('testes@test.com','testtest')
            rv = self.app.post(url_for('auth.request_reset_password'),data={'email' : 'testes@test.com'}, follow_redirects=True)
            self.assertEqual(rv.status_code, 200)
            self.assertIn(b'View Your Classes', rv.data)

    def test_reset(self):
        user = User.query.filter_by(email='testes@test.com').first()
        token = user.reset_token()
        rv = self.app.post(url_for('auth.reset_password', token=token), data={'password':'strongertest','password2':'strongertest'}, follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Don\'t have an account?', rv.data)
        self.assertIn(b'Your password has been successfully updated! You can now login with your new password.', rv.data)


        rv = self.app.post(url_for('auth.login'), data={'email':'testes@test.com', 'password':'strongtest'}, follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Don\'t have an account?', rv.data)
        self.assertIn(b'Invalid username or password', rv.data)
        rv = self.app.post(url_for('auth.login'), data={'email':'testes@test.com', 'password':'strongertest'}, follow_redirects=True)

    def test_register_student(self):
        '''Registration and confirmation of student'''
        with self.app:
            # Register
            response = self.register_student('yolo', 'amirite','patkennedy79@gmail.com', 'FlaskIsAwesome', 'FlaskIsAwesome')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'You have not verified your account. Please check your inbox (and your spam folder) - you should have received an email with a confirmation link.', response.data)
            u = User.query.filter_by(email='patkennedy79@gmail.com').first()
            self.assertEqual(u.firstName, 'yolo')
            self.assertEqual(u.lastName, 'amirite')
            self.assertFalse(u.confirmed)
    
    def test_confirm(self):
        '''Test confirmation of account'''
        with self.app:
            self.register_student('yolo', 'amirite','patkennedy79@gmail.com', 'FlaskIsAwesome', 'FlaskIsAwesome')
            self.login('patkennedy79@gmail.com', 'FlaskIsAwesome')
            u = User.query.filter_by(email='patkennedy79@gmail.com').first()
            token = generate_confirmation_token(u.email)
            # Confirm Token
            response2 = self.app.get(url_for('auth.confirm_email', token=token), follow_redirects=True)
            self.assertEqual(response2.status_code, 200)
            u = User.query.filter_by(email='patkennedy79@gmail.com').first()
            self.assertTrue(u.confirmed)
            self.assertIn(b'You have confirmed your account. Thanks!', response2.data)
            response3 = self.app.get(url_for('auth.confirm_email', token=token), follow_redirects=True)
            self.assertIn(b'Account already confirmed. Please login.', response3.data)
            response4 = self.app.get(url_for('auth.confirm_email', token='lol'))
            self.assertEqual(response4.status_code, 404)

    def test_resend_conf(self):
        '''Resending confirmation email'''
        with self.app:
            # Register
            self.register_student('yolo', 'amirite','patkennedy79@gmail.com', 'FlaskIsAwesome', 'FlaskIsAwesome')
            rv = self.app.get(url_for('auth.resend'), follow_redirects=True)
            self.assertEqual(rv.status_code, 200)
            self.assertIn(b'A new confirmation email has been sent.', rv.data)
            self.assertIn(b'You have not verified your account. Please check your inbox (and your spam folder) - you should have received an email with a confirmation link.',rv.data)

    def test_register_educator(self):
        with self.app:
            response = self.register_educator('yolo', 'amirite','patkennedy79@gmail.com', 'FlaskIsAwesome', 'FlaskIsAwesome')
            self.assertEqual(response.status_code, 200)
            u = User.query.filter_by(email='patkennedy79@gmail.com').first()
            self.assertEqual(u.firstName, 'yolo')
            self.assertEqual(u.lastName, 'amirite')
            self.assertFalse(u.confirmed)

    def test_logout(self):
        '''Login / Logout'''
        with self.app:
            response = self.login('testes@test.com','testtest')
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

    def test_login_home(self):
        '''Login from home page'''
        with self.app:
            rv = self.app.post(url_for('main.home'), data={'login-email' : 'testes@test.com', 'login-password' : 'testtest' }, follow_redirects=True)
            self.assertEqual(rv.status_code, 200)
            self.assertIn(b'Join A Class', rv.data)


    def test_confirmed(self):
        '''Redirect to dashboard, confirmed'''
        with self.app:
            self.login('testes@test.com','testtest')
            response = self.app.get(url_for('auth.unconfirmed'), follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Join A Class', response.data)
            response = self.app.get(url_for('auth.resend'), follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Join A Class', response.data)

    def test_incorrect_login_home(self):
        '''Invalid login from home page'''
        rv = self.app.post(url_for('main.home'), data={'login-email' : 'testes@test.com', 'login-password' : 'wrong' }, follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Invalid username or password', rv.data)
        self.assertIn(b'Don\'t have an account?', rv.data)

    def test_insufficient_char_password(self):
        '''Less than 8 characters in password'''
        rv = self.register_student('yolo', 'amirite','patkennedy79@gmail.com', 'toshort', 'toshort')
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Field must be at least 8 characters long.', rv.data)
        self.assertIn(b'Create A Student Account', rv.data)

if __name__ == '__main__':
    unittest.main()
