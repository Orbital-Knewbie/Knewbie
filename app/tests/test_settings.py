import unittest
from app.tests.basetest import BaseTest
from app.models import *
from app.auth.email import generate_confirmation_token

from flask import url_for
from flask_login import current_user

class SettingsTest(BaseTest):
    def test_knewbie(self):
        '''Change knewbie ID'''
        with self.app:
            self.login('testes@test.com','testtest')
            self.assertEqual(current_user.knewbie_id, '123456')
            rv = self.app.post(url_for('main.settings_knewbie_id'), follow_redirects=True)
            self.assertEqual(rv.status_code, 200)
            self.assertNotEqual(current_user.knewbie_id, '123456')
            self.assertIn(b'Your profile has been successfully updated!', rv.data)

    def test_knewbie_edu(self):
        '''Forbidden knewbie ID (educator)'''
        with self.app:
            self.login('edutest@test.com','strongtest')
            rv = self.app.post(url_for('main.settings_knewbie_id'), follow_redirects=True)
            self.assertEqual(rv.status_code, 403)

    def test_password_change(self):
        '''Successful password change'''
        with self.app:
            self.login('edutest@test.com','strongtest')
            rv = self.app.post(url_for('main.change_pw'), \
                data={'pw-password':'strongtest',
                      'pw-newPassword':'newtesttest',
                      'pw-confirmPassword':'newtesttest'}, \
                          follow_redirects=True)
            self.assertEqual(rv.status_code, 200)
            self.assertIn(b'Your profile has been successfully updated!', rv.data)
            self.assertTrue(current_user.check_password('newtesttest'))

    def test_incorrect_password(self):
        '''Incorrrect current password'''
        with self.app:
            self.login('edutest@test.com','strongtest')
            rv = self.app.post(url_for('main.change_pw'), \
                data={'pw-password':'weaktest',
                      'pw-newPassword':'newtesttest',
                      'pw-confirmPassword':'newtesttest'}, \
                          follow_redirects=True)
            self.assertEqual(rv.status_code, 200)
            self.assertIn(b'Invalid current password, please try again', rv.data)    
            
    def test_reuse_password(self):
        '''Reuse old password'''
        with self.app:
            self.login('edutest@test.com','strongtest')
            rv = self.app.post(url_for('main.change_pw'), \
                data={'pw-password':'strongtest',
                      'pw-newPassword':'strongtest',
                      'pw-confirmPassword':'strongtest'}, \
                          follow_redirects=True)
            self.assertEqual(rv.status_code, 200)
            self.assertIn(b'You cannot reuse your old password. Please choose a different password.', rv.data)

    def test_get_reset_email(self):
        with self.app:
            self.login('edutest@test.com','strongtest')
            rv = self.app.get(url_for('auth.reset_email'), follow_redirects=True)
            self.assertEqual(rv.status_code, 200)
            self.assertIn(b'Enter Current Email For Verification', rv.data)

    def test_post_reset_email(self):
        with self.app:
            self.login('edutest@test.com','strongtest')
            rv = self.app.post(url_for('auth.reset_email'), data={'email':'edutest@test.com'}, follow_redirects=True)
            self.assertEqual(rv.status_code, 200)
            self.assertIn(b'An email has been sent with instructions to reset your email.', rv.data)
            self.assertIn(b'Update and Link new Email', rv.data)


    def test_email_token(self):
        '''Access email reset link'''
        with self.app:
            self.login('edutest@test.com','strongtest')
            token = current_user.reset_token()
            rv = self.app.get(url_for('auth.new_email', token=token), follow_redirects=True)
            self.assertEqual(rv.status_code, 200)
            self.assertIn(b'Update Email', rv.data)

    def test_post_new_email(self):
        '''Submit new email'''        
        with self.app:
            self.login('edutest@test.com','strongtest')
            token = current_user.reset_token()
            self.assertEqual(current_user.email, 'edutest@test.com')
            rv = self.app.post(url_for('auth.new_email', token=token), data={'email':'edutest2@test.com', 'email2':'edutest2@test.com'}, follow_redirects=True)
            self.assertEqual(rv.status_code, 200)
            
            self.assertIn(b'Your email has been successfully updated! You can now login with your new email.', rv.data)
            self.assertEqual(current_user.email, 'edutest2@test.com')

if __name__ == '__main__':
    unittest.main()
