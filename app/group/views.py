"""
Routes and views for the flask application.
"""

from flask import render_template, request, flash, redirect, url_for, jsonify, make_response
from flask_login import current_user, login_user, logout_user, login_required
from flask_mail import Message
from app import db, mail
from app.group import bp
from app.models import User, Question, Option, Response, Group, Thread, Post, Proficiency, Quiz
from app.group.forms import *
from app.base import *
from app.group.group import *
from app.decorator import check_confirmed

import json

# Routes for class
# /class
# join
# create
@bp.route('/join', methods=['POST'])
@login_required
def joinclass():
    if current_user.check_educator():
        return redirect(url_for('dashboard'))
    joinForm = JoinClassForm(prefix='join')
    classForm = NameForm(prefix='class')
    quizForm = NameForm(prefix='quiz')
    image_file = get_image_file(current_user)
    if joinForm.validate_on_submit():
        classCode = joinForm.title.data
        group = validate_code_link(classCode)
        group_add = add_user(group, current_user)
        if group_add is None:
            flash('You are already in the class.')
        return redirect(url_for('forum.forum', groupID=group.id))
    return render_template('dashboard.html', image_file=image_file, classForm=classForm, quizForm=quizForm, joinForm=joinForm)

@bp.route('/create', methods=['POST'])
@login_required
def createclass():
    """Renders the create class page for educators."""
    if not current_user.check_educator():
        return render_template('errors/error403.html'), 403
    classForm = NameForm(prefix='class')
    quizForm = NameForm(prefix='quiz')
    joinForm = JoinClassForm(prefix='join')
    image_file = get_image_file(current_user)
    if classForm.validate_on_submit():
        group = add_group(current_user, classForm.title.data)
        if group is None:
            flash('You have already created a Class with this name. Please choose a different name.', 'warning')
            return redirect(url_for('main.dashboard'))
        return redirect(url_for('group.createclasssuccess', groupID=group.id))
    return render_template('dashboard.html', image_file=image_file, codeForm=codeForm, classForm=classForm, quizForm=quizForm)

# Routes within class
# /<int:groupID>
# success
# user
# leaderboard
# delete
# participants
# participants/<int:userID>/delete
# classquizzes
# edit class settings
@bp.route('/<int:groupID>/success')
@login_required
def createclasssuccess(groupID):
    """Renders the create class was a success page for educators."""
    if not current_user.check_educator():
        return render_template('errors/error403.html'), 403
    group = validate_group_link(current_user, groupID)
    return render_template('group/createclasssuccess.html', title=' | Create Class', group=group)


@bp.route('/<int:groupID>/leaderboard')
@login_required
def leaderboard(groupID):
    """Renders the leaderboard page."""
    group = validate_group_link(current_user, groupID)
    users = get_sorted_students(groupID)
    image_file = get_image_file(current_user)
    return render_template('group/leaderboard.html', image_file=image_file, title=' | Leaderboard', users=users, group=group)

# Routes to delete class
@bp.route('/<int:groupID>/delete', methods=['GET','POST'])
@login_required
def delete_class(groupID):
    if not current_user.check_educator():
        return render_template('errors/error403.html'), 403
    form = DeleteClassForm()
    if form.validate_on_submit():
        group = Group.query.filter_by(id=groupID, classCode = form.title.data).first_or_404()
        remove_all_threads(group)
        remove_group(group)
        flash('Class deleted')
        return redirect(url_for('main.dashboard'))
    return render_template('group/deleteclass.html', title=' | Deactivate Account', form=form)

@bp.route('/<int:groupID>/user', methods=['POST'])
@login_required
def adduserclass(groupID):
    """Renders the create class page for educators."""
    if not current_user.check_educator():
        return render_template('errors/error403.html'), 403
    group = validate_group_link(current_user, groupID)
    joinForm = JoinForm()
    deleteForm = DeleteForm()
    if joinForm.validate_on_submit():
        user = User.query.filter((User.knewbie_id==joinForm.title.data) | (User.email==joinForm.title.data)).first()
        if add_user(group, user):
            flash('User added')
        else:
            flash('User already in Class')
        return redirect(url_for('group.edit_participants', groupID=groupID))

# Routes to edit participants list
@bp.route("/<int:groupID>/participants")
@login_required
def edit_participants(groupID):
    if not current_user.check_educator():
        return render_template('errors/error403.html'), 403
    group = validate_group_link(current_user, groupID)
    users = get_sorted_students(groupID)
    image_file = get_image_file(current_user)
    joinForm = JoinForm()
    deleteForm = DeleteForm()
    return render_template('group/participants.html', title=' | Edit Participants', group=group, image_file=image_file, users=users, deleteForm=deleteForm, joinForm=joinForm)

@bp.route('/<int:groupID>/participants/<int:userID>/delete', methods=['POST'])
@login_required
def delete_participant(groupID, userID):
    if not current_user.check_educator() or current_user.id == userID:
        return render_template('errors/error403.html'), 403
    group = validate_group_link(current_user, groupID)
    user = validate_user_link(groupID, userID)

    joinForm = JoinForm()
    deleteForm = DeleteForm()
    if deleteForm.validate_on_submit():
        remove_user(group, user)
        flash('User deleted')
        return redirect(url_for('group.edit_participants', groupID=groupID))

@bp.route('/<int:groupID>/quizzes')
@login_required
def classquiz(groupID):
    group = validate_group_link(current_user, groupID)
    image_file = get_image_file(current_user)
    quizzes = get_quiz(group)
    user_quizzes = get_user_quizzes(current_user)

    form = None
    if user_quizzes:
        form = QuizCheckForm()
        form.field.choices = list((quiz.id, quiz.name) for quiz in user_quizzes)
    return render_template('group/classquiz.html', title=' | Quiz', group=group, image_file=image_file, quizzes=quizzes, form=form)

@bp.route('/<int:groupID>/quizzes/add', methods=['POST'])
@login_required
def add_class_quiz(groupID):
    group = validate_group_link(current_user, groupID)
    form = QuizCheckForm()
    user_quizzes = get_user_quizzes(current_user)
    form.field.choices = list((quiz.id, quiz.name) for quiz in user_quizzes)
    if form.validate_on_submit():
        quizIDs = form.field.data
        for quizID in quizIDs:
            quiz = validate_quiz_link(current_user, quizID)
            added = add_quiz_group(group, quiz)
            if added is None:
                flash('Quiz ' + quiz.name + ' already added')
        flash('Quizzes added')
    return redirect(url_for('group.classquiz', groupID=groupID))

## UNTESTED FUNCTIONS ##

@bp.route('/<int:groupID>/settings')
@login_required
def class_settings(groupID):
    if not current_user.check_educator():
        return render_template('errors/error403.html'), 403
    group = validate_group_link(current_user, groupID)
    image_file = get_image_file(current_user)
    nameForm = EditNameForm(prefix='name')
    codeForm = UpdateCodeForm(prefix='code')
    return render_template('group/classsettings.html', title=' | Class Settings', group=group, groupID=groupID, image_file=image_file, nameForm=nameForm, codeForm=codeForm)


@bp.route('/<int:groupID>/edit', methods=['POST'])
@login_required
def edit_class_name(groupID):
    """Routing to update Class Name"""
    if not current_user.check_educator():
        return render_template('errors/error403.html'), 403
    group = validate_group_link(current_user, groupID)
    image_file = get_image_file(current_user)
    nameForm = EditNameForm(prefix='name')
    codeForm = UpdateCodeForm(prefix='code')
    if nameForm.validate_on_submit():
        group.name = nameForm.title.data
        db.session.commit()
        flash('Class Name Changed')
    return redirect(url_for('forum.forum', groupID=groupID))

@bp.route('/<int:groupID>/code', methods=['POST'])
@login_required
def update_class_code(groupID):
    """Routing to update Class Code"""
    if not current_user.check_educator():
        return render_template('errors/error403.html'), 403
    group = validate_group_link(current_user, groupID)
    nameForm = EditNameForm(prefix='name')
    codeForm = UpdateCodeForm(prefix='code')
    if codeForm.validate_on_submit():
        group = validate_group_link(current_user, groupID)
        set_class_code(group)
        db.session.commit()
        flash('Your class code has been successfully updated!', 'success')
    return redirect(url_for('forum.forum', groupID=groupID))
