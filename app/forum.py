from flask_login import current_user
from app import db
from app.models import Group, UserGroup, Post, Thread, User
from datetime import datetime

def validate_group_link(groupID):
    group = Group.query.filter_by(id=groupID).first_or_404()
    if UserGroup.query.filter_by(userID=current_user.id, groupID=groupID).first() is not None:
        return group

def save_post(form, threadID):
    post = Post(userID=current_user.id, threadID=threadID, 
                timestamp=datetime.now(), content=form.post.data)
    db.session.add(post)
    db.session.commit()


def create_group(user, name):
    group = Group(name=name)
    db.session.add(group)
    db.session.flush()
    add_participant(user, group)
    
    db.session.commit()
    return group

def add_participant(user, group):
    usergroup = UserGroup(userID=user.id,groupID=group.id)
    db.session.add(usergroup)
    db.session.commit()
    return usergroup

def create_thread(user, group, title, content):
    thread = Thread(groupID=group.id,timestamp=datetime.now(), title=title)
    db.session.add(thread)
    db.session.flush()

    post = Post(userID=user.id, threadID=thread.id, timestamp=datetime.now(), content=content)
    
    db.session.add(post)
    db.session.commit()

def add_test_forum():
    clear_test_forum()
    user = User.query.first()
    group = create_group(user, "first")
    add_participant(user, group)
    create_thread(user, group, "first thread", "first post")

def clear_test_forum():
    g = Group.query.all()
    ug = UserGroup.query.all()
    t = Thread.query.all()
    p = Post.query.all()
    g.extend(ug)
    g.extend(t)
    g.extend(p)
    for i in g:
        db.session.delete(i)
    db.session.commit()

add_test_forum()