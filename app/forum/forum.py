from flask import redirect, url_for, flash
from app import db
from app.models import Group, Post, Thread, User, Quiz
from app.group.group import validate_group_link
from datetime import datetime


def validate_post_link(user, groupID, threadID, postID):
    # Check validity of link access first
    group = validate_group_link(user, groupID)
    if group is None:
        return 
    thread = Thread.query.filter_by(id=threadID,groupID=groupID).first_or_404()
    post = Post.query.filter_by(id=postID,threadID=threadID).first_or_404()
    if user.id != post.userID and user.urole != 'educator':
        return 
    return post

def save_post(user, content, threadID):
    post = Post(user=user, threadID=threadID, 
                timestamp=datetime.now(), content=content)
    db.session.add(post)
    db.session.commit()
    flash('Your post is now live!')
    return post

def remove_post(post):
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted')

def add_thread(user, group, title, content):
    thread = Thread(group=group,timestamp=datetime.now(), title=title)
    db.session.add(thread)
    db.session.flush()

    post = save_post(user, content, thread.id)
    
    db.session.add(post)
    db.session.commit()
    return thread

def remove_thread(thread):
    for p in Post.query.filter_by(threadID=thread.id).all():
        db.session.delete(p)
    db.session.delete(thread)
    db.session.commit()

def get_post_users(posts):
    '''Return user names as userID, name pairs in a dictionary'''
    users = {}
    for post in posts:
        if post.userID in users: continue
        user = User.query.filter_by(id=post.userID).first()
        users[post.userID] = ' '.join((user.firstName,user.lastName))
    return users

