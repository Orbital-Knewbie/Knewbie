"""
The flask application package.
"""
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail

from install import org_qns
from catsim.cat import generate_item_bank

naming_convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}



app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app=app, metadata=MetaData(naming_convention=naming_convention))
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
mail = Mail(app)

from app import models

db.create_all()

def add_qn(org_qns):
    '''Adds questions to the database, where questions are formatted to be in a dictionary
    {<question>:{'answer':<options>,'difficulty':<difficulty>}
    <questions> is str
    <options> is list of str
    <difficulty> is float (not added yet)
    '''
    
    for q in org_qns.keys():
        item = generate_item_bank(1)[0]
        qn = models.Question(question=q, discrimination=item[0], \
                    difficulty=item[1], guessing=item[2], upper=item[3], topicID=1)
        user = models.User.query.filter_by(admin=True).first()
        qn.userID = user.id
        db.session.add(qn)
        db.session.commit()
        qid = qn.id
        b=True
        for o in org_qns[q]['answers']:
            opt=models.Option(qnID=qid,option=o)
            db.session.add(opt)
            if b:
                db.session.flush()
                qn.answerID = opt.id
                
                b=False
            
            db.session.commit()

if db.session.query(models.User).count() == 0:
    user = models.User(admin=True)
    db.session.add(user)
if db.session.query(models.Topic).count() == 0:
    for topic in ('General', 'Estimation', 'Geometry', 'Model'):
        db.session.add(models.Topic(name=topic))
if db.session.query(models.Question).count() == 0:
    add_qn(org_qns)


from app import views
from app.errors.handlers import errors

app.register_blueprint(errors)

if __name__ == '__main__':
    app.run(debug=True)



