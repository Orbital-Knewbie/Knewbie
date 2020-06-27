import unittest
from app.tests.basetest import BaseTest
from app.models import *
from flask import url_for

class AuthTest(BaseTest):
    def test_deactivate(self):
        with self.app:
            self.login('testes@test.com','test')
            rv = self.app.post(url_for('request_deactivate'), data={'email':'testes@test.com'}, follow_redirects=True)
            self.assertEqual(rv.status_code, 200)
            user = User.query.filter_by(email='testes@test.com').first()
            token = user.reset_token()
            rv = self.app.get(url_for('deactivate_account', token=token), follow_redirects=True)
            self.assertEqual(rv.status_code, 200)
            self.assertIn(b'Your account has been successfully deactivated! Thank you.', rv.data)
            self.assertIn(b'Knowledge is Power. Even if you are a Noobie.', rv.data)
            user = User.query.filter_by(email='testes@test.com').first()
            self.assertIsNone(user)

    def test_reset_authenticated(self):
        with self.app:
            self.login('testes@test.com','test')
            rv = self.app.get(url_for('request_reset_password'), follow_redirects=True)
            self.assertEqual(rv.status_code, 200)
            self.assertIn(b'View Your Classes', rv.data)

    def test_reset(self):
        user = User.query.filter_by(email='testes@test.com').first()
        token = user.reset_token()
        rv = self.app.post(url_for('reset_password', token=token), data={'password':'strongertest','password2':'strongertest'}, follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Don\'t have an account?', rv.data)
        self.assertIn(b'Your password has been successfully updated! You can now login with your new password.', rv.data)


        rv = self.app.post(url_for('login'), data={'email':'testes@test.com', 'password':'strongtest'}, follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Don\'t have an account?', rv.data)
        self.assertIn(b'Invalid username or password', rv.data)
        rv = self.app.post(url_for('login'), data={'email':'testes@test.com', 'password':'strongertest'}, follow_redirects=True)


if __name__ == '__main__':
    unittest.main()
