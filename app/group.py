from app import db
from app.models import User, Group
from flask_login import current_user

def validate_group_link(groupID):
    return Group.query.filter_by(id=groupID).filter(Group.users.any(id=current_user.id)).first_or_404()

def validate_code_link(classCode):
    return Group.query.filter_by(classCode=classCode).first_or_404()

def validate_user_link(groupID, userID):
    return User.query.filter_by(id=userID).filter(User.groups.any(id=groupID)).first_or_404()

def get_sorted_students(groupID):
    return User.query.filter_by(urole='student').\
        filter(User.groups.any(id=groupID)).order_by(User.curr_theta.desc()).all()

def add_group(name):
    group = Group(name=name)
    set_class_code(group)
    group.users.append(current_user)
    db.session.add(group)
    db.session.commit()

def add_user(group, user):
    if user in group.users: return #prevent duplicates
    group.users.append(user)
    db.session.commit()
    return group

def remove_user(group, user):
    group.users.remove(user)
    db.session.commit()

def remove_group(group):
    group.users = []
    db.session.delete(group)
    db.session.commit()