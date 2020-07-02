# project/test_basic.py
 
 
import os
import unittest

from app.tests.basetest import BaseTest
from flask import url_for
from app import db, mail
from app.models import *
basedir = os.path.abspath(os.path.dirname(__file__))
 
 
TEST_DB = 'test.db'
 
 
class BasicTests(BaseTest):
 
    ###############
    #### tests ####
    ###############
 
    def test_main_page(self):
        '''Pages without User attributes'''
        #pages = ('/','/faq', '/contact', '/register', '/login', '/dashboard', '/resetpassword', '/deactivate')
        pages = ('main.home','main.faq','main.contact','auth.reg','auth.login','main.dashboard','auth.request_reset_password', 'auth.request_deactivate')
        for page in pages:
            response = self.app.get(url_for(page), follow_redirects=True)
            self.assertEqual(response.status_code, 200)
    
    def test_post_register(self):
        '''GET requests to POST-only pages'''
        pages = ('auth.regstu', 'auth.regedu', 'group.joinclass', 'group.createclass', 'quiz.createquiz')
        for page in pages:
            response = self.app.get(url_for(page), follow_redirects=True)
            self.assertEqual(response.status_code, 405)

    def test_report_unauthenticated(self):
        '''Unauthenticated access of progress report'''
        response = self.app.get(url_for('main.get_report'), follow_redirects=True)
        self.assertIn(b'Sign In', response.data)
        self.assertIn(b'Don\'t have an account?', response.data)
        self.assertIn(b'Forgot your password?', response.data)

    def test_get_user_report(self):
        '''Access user report of existing user'''
        response = self.app.get(url_for('main.progressreport', knewbieID='123456'), follow_redirects=True)
        self.assertIn(b'<div class="chart-container" style="text-align: center;">\n    <canvas id="myChart" style="margin: 0 auto; width: 100vw !important; height: 40vh !important;"></canvas>\n</div>', response.data)
       
    def test_get_no_report(self):
        '''Access user report of non-existant user'''
        response = self.app.get(url_for('main.progressreport', knewbieID='246810'), follow_redirects=True)
        self.assertEqual(response.status_code, 404)

    def test_send_contact(self):
        '''Send a contact form'''
        rv = self.app.post(url_for('main.contact'), data={'email': 'contact@test.com', 'name':'name', 'subject':'subject', 'message' : 'message'}, follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Thank you for your message. We\'ll get back to you shortly.', rv.data)
        
 
if __name__ == "__main__":
    unittest.main()