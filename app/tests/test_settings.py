import unittest
from app.tests.basetest import BaseTest
from app.models import *

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

if __name__ == '__main__':
    unittest.main()
