import unittest, os
from app import app, db, mail
from app.models import User, Post
from app.email import register

basedir = os.path.abspath(os.path.dirname(__file__))

TEST_DB = 'test.db'

class UserModelCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
            os.path.join(basedir, TEST_DB)
        self.app = app.test_client()
        db.drop_all()
        db.create_all()
 
        # Disable sending emails during unit testing
        mail.init_app(app)
        self.assertEqual(app.debug, False)

    def tearDown(self):
        db.session.remove()
        db.drop_all()

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
            data=dict(email=email, password=password),
            follow_redirects=True
        )
 
    def logout(self):
        return self.app.get(
            '/logout',
            follow_redirects=True
        )

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

    #def test_invalid_user_registration_duplicate_email(self):
    #    response = self.register_student('yolo', 'amirite','patkennedy79@gmail.com', 'FlaskIsAwesome', 'FlaskIsAwesome')
    #    self.assertEqual(response.status_code, 200)
    #    response = self.register_student('yolo', 'amirite','patkennedy79@gmail.com', 'FlaskIsReallyAwesome', 'FlaskIsReallyAwesome')
    #    self.assertIn(b'ERROR! Email (patkennedy79@gmail.com) already exists.', response.data)

if __name__ == '__main__':
    unittest.main()
