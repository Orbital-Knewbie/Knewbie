"""
Routes and views for the flask application.
"""

from flask import render_template, request, flash, redirect, url_for, jsonify, make_response
from flask_login import current_user, login_user, logout_user, login_required
from flask_mail import Message
from app import db, mail
from app.forum import bp
from app.models import User, Question, Option, Response, Group, Thread, Post, Proficiency, Quiz
from app.forum.forms import *
from app.base import *
from app.forum.forum import *
from app.decorator import check_confirmed

# Routes for Class Forum
# forum
# forum/thread
# forum/thread/<int:threadID>
# forum/thread/<int:threadID>/delete
# forum/thread/<int:threadID>/<int:postID>/delete
# forum/thread/<int:threadID>/<int:postID>/edit
@bp.route('/<int:groupID>')
@bp.route('/<int:groupID>/forum')
@login_required
def forum(groupID):
    group = validate_group_link(current_user, groupID)
    if group is None:
        return redirect(url_for('main.dashboard'))
    threads = Thread.query.filter_by(groupID=groupID).all()
    image_file = get_image_file(current_user)
    return render_template('forum/forum.html', title=' | Forum', groupID=groupID, threads=threads, group=group, image_file=image_file)

@bp.route('/<int:groupID>/forum/thread', methods=['GET','POST'])
@login_required
def create_thread(groupID):
    # Check validity of link access first
    group = validate_group_link(current_user, groupID)

    # Render ThreadForm
    form = ThreadForm()

    # POST request for new thread
    if form.validate_on_submit():
        thread = add_thread(current_user, group, form.title.data, form.content.data)     
        return redirect(url_for('forum.forum_post', groupID=groupID, threadID=thread.id))

    # GET request for create thread
    return render_template('forum/posts.html', title=' | Forum', postForm=form)

@bp.route('/<int:groupID>/forum/thread/<int:threadID>', methods=['GET', 'POST'])
@login_required
def forum_post(groupID, threadID):
    # Check validity of link access first
    group = validate_group_link(current_user, groupID)
    thread = Thread.query.filter_by(groupID=groupID,id=threadID).first_or_404()

    # Render Posts and PostForm
    posts = Post.query.filter_by(threadID=threadID).all()
    users = get_post_users(posts)

    postForm = PostForm()
    delThreadForm = DeleteForm(prefix="thread")
    delPostForm = DeleteForm(prefix="post")

    # POST request for new post
    if postForm.validate_on_submit():
        save_post(current_user, postForm.content.data, threadID)
        return redirect(url_for('forum.forum_post',groupID=groupID,threadID=threadID))
    
    # GET request for forum thread
    return render_template('forum/posts.html', title=' | Forum', thread=thread,posts=posts, postForm=postForm, delThreadForm=delThreadForm, delPostForm=delPostForm, users=users)

@bp.route('/<int:groupID>/forum/thread/<int:threadID>/delete', methods=['POST'])
@login_required
def delete_thread(groupID, threadID):
    # Check validity of link access first
    if not current_user.check_educator():
        return render_template('errors/error403.html'), 403

    group = validate_group_link(current_user, groupID)
    thread = Thread.query.filter_by(groupID=groupID,id=threadID).first_or_404()

    postForm = PostForm()
    delThreadForm = DeleteForm(prefix="thread")
    delPostForm = DeleteForm(prefix="post")

    if delThreadForm.validate_on_submit():
        remove_thread(thread)
        flash('Thread deleted')
        return redirect(url_for('forum.forum', groupID=groupID))

@bp.route('/<int:groupID>/forum/thread/<int:threadID>/<int:postID>/delete', methods=['POST'])
@login_required
def delete_post(groupID, threadID, postID):
    # Check validity of link access first
    post = validate_post_link(current_user, groupID,threadID,postID)
    if post is None:
        return render_template('errors/error403.html'), 403
    postForm = PostForm()
    delThreadForm = DeleteForm(prefix="thread")
    delPostForm = DeleteForm(prefix="post")
    if delPostForm.validate_on_submit():
        remove_post(post)
        return redirect(url_for('forum.forum_post', groupID=groupID,threadID=threadID))

@bp.route('/<int:groupID>/forum/thread/<int:threadID>/<int:postID>/edit', methods=['GET','POST'])
@login_required
def edit_post(groupID,threadID,postID):
    # Check validity of link access first
    post = validate_post_link(current_user, groupID,threadID,postID)
    if post is None:
        return render_template('errors/error403.html'), 403

    form = PostForm()
    if request.method == 'GET':
        form.content.data=post.content

    if form.validate_on_submit():
        post.content = form.content.data
        db.session.commit()
        return redirect(url_for('forum.forum_post', groupID=groupID,threadID=threadID))

    return render_template('forum/posts.html', title=' | Forum', postForm=form, editpost=post)
