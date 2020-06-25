import unittest, os
from flask import url_for
from flask_login import current_user
from app import app, db, mail
from app.models import User, Post
from app.profile import register
from app.email import generate_confirmation_token

basedir = os.path.abspath(os.path.dirname(__file__))

TEST_DB = 'test.db'

class UserModelCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
            os.path.join(basedir, TEST_DB)
        app.login_manager.init_app(app)
        self.app = app.test_client()

        ## IMPORTANT FOR LOGIN ##
        app.test_request_context().push()

        db.session.remove()
        db.drop_all()
        db.create_all()
        self.add_test_user()
        self.add_test_edu()
        db.session.commit()
 
        # Disable sending emails during unit testing
        mail.init_app(app)
        self.assertEqual(app.debug, False)

    def tearDown(self):
        pass

    ########################
    #### helper methods ####
    ########################

    def register(self, role, *rdata):
        fields=('firstName', 'lastName', 'email', 'password', 'password2')
        pre = role[:3] + '-'
        data = {}
        for i in range(len(fields)):
            data[pre+fields[i]] = rdata[i]
        return self.app.post(
            '/register/' + role,
            data=data,
            follow_redirects=True
        )
 
    def register_student(self, *data):
        return self.register('student', *data)

    def register_educator(self, *data):
        return self.register('educator', *data)
        
 
    def login(self, email, password):

        return self.app.post(
            '/login',
            data={'email' : email, 'password' : password },
            follow_redirects=True
        )
 
    def logout(self):
        return self.app.get(
            '/logout',
            follow_redirects=True
        )

    def add_test_user(self):
        u = User(firstName="first", lastName="last", email="test@test.com", \
            urole="student", knewbie_id="123456", curr_theta=-1.33, confirmed=True)
        u.set_password("strongpassword")
        db.session.add(u)

    def add_test_edu(self):
        u = User(firstName="first", lastName="last", email="edu@test.com", \
            urole="educator", confirmed=True)
        u.set_password("weakpassword")
        db.session.add(u)

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
            response = self.login('test@test.com','strongpassword')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Join A Class', response.data)
            response2 = self.logout()
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Knowledge is Power. Even if you are a Noobie.', response2.data)
            response = self.login('edu@test.com','weakpassword')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Create A New Class', response.data)
            self.assertIn(b'Create A New Quiz', response.data)
            response2 = self.logout()
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Knowledge is Power. Even if you are a Noobie.', response2.data)

    def test_confirmed(self):
        '''Redirect to dashboard, confirmed'''
        with self.app:
            self.login('test@test.com','strongpassword')
            response = self.app.get(url_for('unconfirmed'), follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Join A Class', response.data)
            response = self.app.get(url_for('resend'), follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Join A Class', response.data)
        


if __name__ == '__main__':
    unittest.main()
