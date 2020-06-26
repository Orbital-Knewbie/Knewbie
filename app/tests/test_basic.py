# project/test_basic.py
 
 
import os
import unittest
 
from app import app, db, mail
from app.models import *
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
        self.app = app.test_client()

        ## IMPORTANT FOR LOGIN ##
        app.test_request_context().push()

        db.session.remove()
        db.drop_all()
        db.create_all()
        self.add_test_user()

        # Disable sending emails during unit testing
        mail.init_app(app)
        self.assertEqual(app.debug, False)
 
    # executed after each test
    def tearDown(self):
        pass
    
    ########################
    #### helper methods ####
    ########################
    def add_test_user(self):
        u = User(firstName="first", lastName="last", email="test@test.com", \
            urole="student", knewbie_id="123456", curr_theta=-1.33, confirmed=True)
        u.set_password("test")
        db.session.add(u)
        db.session.commit()
 
    ###############
    #### tests ####
    ###############
 
    def test_main_page(self):
        '''Pages without User attributes'''
        pages = ('/','/faq', '/contact', '/register', '/login', '/dashboard', '/resetpassword', '/deactivate')
        for page in pages:
            response = self.app.get(page, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
    
    def test_post_register(self):
        '''GET requests to POST-only pages'''
        pages = ('/register/student', '/register/educator', '/class/join', '/class/create', '/quiz/create')
        for page in pages:
            response = self.app.get(page, follow_redirects=True)
            self.assertEqual(response.status_code, 405)

    def test_report_unauthenticated(self):
        '''Unauthenticated access of progress report'''
        response = self.app.get('/progressreport', follow_redirects=True)
        self.assertIn(b'Sign In', response.data)
        self.assertIn(b'Don\'t have an account?', response.data)
        self.assertIn(b'Forgot your password?', response.data)

    def test_get_user_report(self):
        '''Access user report of existing user'''
        response = self.app.get('/progressreport/123456', follow_redirects=True)
        self.assertIn(b'<div class="chart-container" style="text-align: center;">\n    <canvas id="myChart" style="margin: 0 auto; width: 100vw !important; height: 40vh !important;"></canvas>\n</div>', response.data)
       
    def test_get_no_report(self):
        '''Access user report of non-existant user'''
        response = self.app.get('/progressreport/246810', follow_redirects=True)
        self.assertEqual(response.status_code, 404)

 
if __name__ == "__main__":
    unittest.main()