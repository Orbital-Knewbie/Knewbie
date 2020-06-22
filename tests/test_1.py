import unittest
from app import app, db
from app.models import User, Post

class UserModelCase(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_password_hashing(self):
        u = User(firstName='ramana')
        u.set_password('ramanalovesfootball')
        self.assertFalse(u.check_password('ramanalovesmaplestory'))
        self.assertTrue(u.check_password('ramanalovesfootball'))

if __name__ == '__main__':
    unittest.main()
