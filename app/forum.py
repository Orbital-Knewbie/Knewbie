from flask import redirect, url_for
from flask_login import current_user
from app import db
from app.models import Group, Post, Thread, User, Quiz
from app.profile import set_class_code
from datetime import datetime

def validate_group_link(groupID):
    return Group.query.filter_by(id=groupID).filter(Group.users.any(id=current_user.id)).first_or_404()

def validate_code_link(classCode):
    return Group.query.filter_by(classCode=classCode).first_or_404()

def validate_post_link(groupID, threadID, postID):
    # Check validity of link access first
    group = validate_group_link(groupID)
    if group is None:
        return 
    thread = Thread.query.filter_by(id=threadID,groupID=groupID).first_or_404()
    post = Post.query.filter_by(id=postID,threadID=threadID).first_or_404()
    if current_user.id != post.userID and current_user.urole != 'educator':
        return 
    return post

def save_post(form, threadID):
    post = Post(user=current_user, threadID=threadID, 
                timestamp=datetime.now(), content=form.post.data)
    db.session.add(post)
    db.session.commit()


def create_group(user, name):
    group = Group(name=name)
    set_class_code(group)
    add_participant(user, group)
    
    db.session.commit()
    return group

def add_participant(user, group):
    group.users.append(user)
    db.session.add(group)

def create_thread(user, group, title, content):
    thread = Thread(group=group,timestamp=datetime.now(), title=title)
    db.session.add(thread)
    db.session.flush()

    post = Post(user=user, thread=thread, timestamp=datetime.now(), content=content)
    
    db.session.add(post)
    db.session.commit()

def add_test_forum():
    clear_test_forum()
    user = User.query.first()
    if user is None: return
    group = create_group(user, "first")
    add_participant(user, group)
    create_thread(user, group, "first thread", "first post")

def clear_test_forum():
    g = Group.query.all()
    t = Thread.query.all()
    p = Post.query.all()
    q = Quiz.query.all()
    g.extend(t)
    g.extend(p)
    g.extend(q)
    for i in g:
        db.session.delete(i)
    db.session.commit()

add_test_forum()

def get_post_users(posts):
    '''Return user names as userID, name pairs in a dictionary'''
    users = {}
    for post in posts:
        if post.userID in users: continue
        user = User.query.filter_by(id=post.userID).first()
        users[post.userID] = ' '.join((user.firstName,user.lastName))
    return users