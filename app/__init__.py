#"""
#The flask application package.
#"""
#from flask import Flask
#from config import Config
#from flask_sqlalchemy import SQLAlchemy
#from sqlalchemy import MetaData
#from flask_migrate import Migrate
#from flask_login import LoginManager
#from flask_mail import Mail

#from install import org_qns
#from catsim.cat import generate_item_bank

#naming_convention = {
#    "ix": 'ix_%(column_0_label)s',
#    "uq": "uq_%(table_name)s_%(column_0_name)s",
#    "ck": "ck_%(table_name)s_%(column_0_name)s",
#    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
#    "pk": "pk_%(table_name)s"
#}


"""
The flask application package.
"""
import logging, os
from logging.handlers import SMTPHandler, RotatingFileHandler
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail

naming_convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

db = SQLAlchemy(metadata=MetaData(naming_convention=naming_convention))
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = 'Please log in to access this page.'
mail = Mail()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    #### IMPORTANT ####
    app.app_context().push()

    db.init_app(app)
    with app.app_context():
        if db.engine.url.drivername == 'sqlite':
            migrate.init_app(app, db, render_as_batch=True)
        else:
            migrate.init_app(app, db)
        db.create_all()
    login.init_app(app)
    mail.init_app(app)

    initialize_blueprints(app)

    if not app.debug and not app.testing:
        if app.config['MAIL_SERVER']:
            auth = None
            if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
                auth = (app.config['MAIL_USERNAME'],
                        app.config['MAIL_PASSWORD'])
            secure = None
            if app.config['MAIL_USE_TLS']:
                secure = ()
            mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                fromaddr='no-reply@' + app.config['MAIL_SERVER'],
                toaddrs=app.config['ADMINS'], subject='Knewbie Failure',
                credentials=auth, secure=secure)
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)

        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/knewbie.log',
                                           maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Knewbie startup')

    return app

def initialize_blueprints(app):
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.errors import errors
    app.register_blueprint(errors)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.group import bp as group_bp
    app.register_blueprint(group_bp, url_prefix='/class')    
    
    from app.forum import bp as forum_bp
    app.register_blueprint(forum_bp, url_prefix='/class')

    from app.quiz import bp as quiz_bp
    app.register_blueprint(quiz_bp, url_prefix='/quiz')


#app = Flask(__name__)
#app.config.from_object(Config)
#db = SQLAlchemy(app=app, metadata=MetaData(naming_convention=naming_convention))
#migrate = Migrate(app, db)
#login = LoginManager(app)
#login.login_view = 'login'
#mail = Mail(app)

#from app import models

#db.create_all()

#def add_qn(org_qns):
#    '''Adds questions to the database, where questions are formatted to be in a dictionary
#    {<question>:{'answer':<options>,'difficulty':<difficulty>}
#    <questions> is str
#    <options> is list of str
#    <difficulty> is float (not added yet)
#    '''
    
#    for q in org_qns.keys():
#        item = generate_item_bank(1)[0]
#        qn = models.Question(question=q, discrimination=item[0], \
#                    difficulty=item[1], guessing=item[2], upper=item[3], topicID=1)
#        user = models.User.query.filter_by(admin=True).first()
#        qn.userID = user.id
#        db.session.add(qn)
#        db.session.commit()
#        qid = qn.id
#        b=True
#        for o in org_qns[q]['answers']:
#            opt=models.Option(qnID=qid,option=o)
#            db.session.add(opt)
#            if b:
#                db.session.flush()
#                qn.answerID = opt.id
                
#                b=False
            
#            db.session.commit()

#if db.session.query(models.User).count() == 0:
#    user = models.User(admin=True)
#    db.session.add(user)
#if db.session.query(models.Topic).count() == 0:
#    for topic in ('General', 'Estimation', 'Geometry', 'Model'):
#        db.session.add(models.Topic(name=topic))
#if db.session.query(models.Question).count() == 0:
#    add_qn(org_qns)


#from app import views
#from app.errors import errors

#app.register_blueprint(errors)

if __name__ == '__main__':
    app.run(debug=True)



