from app import db
from app.models import User, Group



def get_sorted_students(groupID):
    return User.query.filter_by(urole='student').\
        filter(User.groups.any(id=groupID)).order_by(User.curr_theta.desc()).all()

def add_group(name):
    group = Group(name=name)
    set_class_code(group)
    db.session.add(group)
    db.session.commit()

def add_user(group, user):
    group.users.append(user)
    db.session.commit()

def remove_user(group, user):
    group.users.remove(user)
    db.session.commit()

def remove_group(group):
    group.users = []
    db.session.delete(group)
    db.session.commit()