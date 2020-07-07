import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SECURITY_PASSWORD_SALT = 'my_precious_two'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    #MAIL_SERVER = os.environ.get('MAIL_SERVER')
    #MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    #MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    #MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'testflask202005@gmail.com'
    ADMINS = ['testflask202005@gmail.com']


TEST_DB = 'test.db'

class TestingConfig(object):
    TESTING = True
    WTF_CSRF_ENABLED = False
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SECURITY_PASSWORD_SALT = 'my_precious_two'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, TEST_DB)

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    #MAIL_SERVER = os.environ.get('MAIL_SERVER')
    #MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    #MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    #MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'testflask202005@gmail.com'
    ADMINS = ['testflask202005@gmail.com']