"""
Routes and views for the flask application.
"""

from flask import render_template, request, jsonify, flash, redirect, url_for
from flask_login import current_user, login_user, logout_user, login_required
from app import app, db, mail
from app.models import User, Question, Option, Response, Group, Thread, Post, Proficiency, Quiz
from app.forms import *
from app.questions import get_question_options, submit_response, get_student_cat, get_response_answer, get_question_quiz, edit_question
from app.questions import add_quiz, add_question, add_question_quiz, get_topic, validate_quiz_link, get_leaderboard, validate_qn_link, validate_quiz_stu
from app.email import register, resend_conf, send_contact_email, send_reset_email, send_deactivate_email
from app.profile import update_image, set_knewbie_id, set_class_code
from app.forum import save_post, validate_post_link, get_post_users, remove_thread
from app.group import validate_group_link, validate_code_link, validate_user_link, add_user, remove_user, remove_group, add_group
from app.token import confirm_token
from app.decorator import check_confirmed
from app.cat import Student
from flask_mail import Message
import json, datetime
import os
import secrets


# Route for main page functionalities
@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def home():
    """Renders the home page."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    loginForm = LoginForm(prefix='login')
    codeForm = CodeForm(prefix='code')
    if loginForm.validate_on_submit():
        user = User.query.filter_by(email=loginForm.email.data).first()
        if user is None or not user.check_password(loginForm.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user)
        return redirect(url_for('dashboard'))

    return render_template('index.html', loginForm=loginForm, codeForm=codeForm)


@app.route('/progressreport', methods=['GET', 'POST'])
def get_report():
    """Renders the report page."""
    loginForm = LoginForm(prefix='login')
    codeForm = CodeForm(prefix='code')
    if request.method == 'GET':
        return redirect(url_for('progressreport'))
    if codeForm.validate_on_submit():
        return redirect(url_for('progressreport',knewbieID=codeForm.title.data))

@app.route('/progressreport/')
@app.route('/progressreport/<knewbieID>')
def progressreport(knewbieID=None):
    if knewbieID is None:
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        elif current_user.urole == 'educator':
            return redirect(url_for('dashboard'))
        user = current_user
    else:
        user = User.query.filter_by(knewbie_id=knewbieID).first_or_404()
    return render_template('report.html', title=' | Progress Report', user=user)

@app.route('/dashboard')
@login_required
def dashboard():
    """Renders the dashboard page."""
    joinForm = CodeForm(prefix='code')
    classForm = NameForm(prefix='class')
    quizForm = NameForm(prefix='quiz')
    image_file = url_for('static', filename='resources/images/profile_pics/' + current_user.image_file)
    return render_template('dashboard.html', image_file=image_file, classForm=classForm, quizForm=quizForm, joinForm=joinForm)

@app.route('/class/<int:groupID>/leaderboard')
@login_required
def leaderboard(groupID):
    """Renders the leaderboard page."""
    group = validate_group_link(groupID)
    users = get_leaderboard(groupID)
    image_file = url_for('static', filename='resources/images/profile_pics/' + current_user.image_file)
    return render_template('leaderboard.html', image_file=image_file, title=' | Leaderboard', users=users, group=group)

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """Renders the settings page."""
    form = UpdateProfileForm()
    if form.validate_on_submit():            
        if form.image.data:
            image_file = update_image(form.image.data)
            current_user.image_file = image_file
        current_user.firstName = form.firstName.data
        current_user.lastName = form.lastName.data
        db.session.commit()
        flash('Your profile has been successfully updated!', 'success')
        return redirect(url_for('settings'))
    elif request.method == 'GET':
        form.firstName.data = current_user.firstName
        form.lastName.data = current_user.lastName
    image_file = url_for('static', filename='resources/images/profile_pics/' + current_user.image_file)
    return render_template('settings.html', title=' | Settings', image_file=image_file, form=form)

@app.route('/settings/knewbieID')
@login_required
def settings_knewbie_id():
    """Routing to update Knewbie ID"""
    temp = set_code(8)
    while User.query.filter_by(knewbie_id=temp).first() is not None:
        temp = set_code(8)
    db.session.commit()
    flash('Your profile has been successfully updated!', 'success')
    return redirect(url_for('settings'))


@app.route('/faq')
def faq():
    """Renders the faq page."""
    return render_template('faq.html', title=' | FAQ')

@app.route('/class/join', methods=['POST'])
@login_required
def joinclass():
    if current_user.check_educator():
        return redirect(url_for('dashboard'))
    joinForm = CodeForm(prefix='code')
    classForm = NameForm(prefix='class')
    quizForm = NameForm(prefix='quiz')
    image_file = url_for('static', filename='resources/images/profile_pics/' + current_user.image_file)
    if joinForm.validate_on_submit():
        classCode = joinForm.title.data
        group = validate_code_link(classCode)
        add_user(group, current_user)
        return redirect(url_for('forum', groupID=group.id))
    return render_template('dashboard.html', image_file=image_file, classForm=classForm, quizForm=quizForm, joinForm=joinForm)

@app.route('/class/create', methods=['POST'])
@login_required
def createclass():
    """Renders the create class page for educators."""
    if not current_user.check_educator():
        return render_template('error404.html'), 404
    classForm = NameForm(prefix='class')
    quizForm = NameForm(prefix='quiz')
    codeForm = CodeForm(prefix='code')
    image_file = url_for('static', filename='resources/images/profile_pics/' + current_user.image_file)
    if classForm.validate_on_submit():
        add_group(classForm.title.data)
        return redirect(url_for('createclasssuccess', groupID=group.id))
    return render_template('dashboard.html', image_file=image_file, codeForm=codeForm, classForm=classForm, quizForm=quizForm)

@app.route('/class/<int:groupID>/success')
@login_required
def createclasssuccess(groupID):
    """Renders the create class was a success page for educators."""
    group = validate_group_link(groupID)
    return render_template('createclasssuccess.html', title=' | Create Class', group=group)

@app.route('/class/<int:groupID>/user', methods=['POST'])
@login_required
def adduserclass(groupID):
    """Renders the create class page for educators."""
    if not current_user.check_educator():
        return render_template('error404.html'), 404
    group = validate_group_link(groupID)
    form = JoinForm()
    if form.validate_on_submit():
        user = User.query.filter_by(knewbie_id=form.title.data).first_or_404()
        if add_user(group, user):
            flash('User added')
        else:
            flash('User already in Class')
        return redirect(url_for('forum', groupID=groupID))

@app.route('/quiz/<int:quizID>')
@login_required
def preview_quiz(quizID):
    """Renders the preview quiz page for educators."""
    if not current_user.check_educator():
        return render_template('error404.html'), 404
    quiz = validate_quiz_link(quizID)
    questions = get_question_quiz(quiz)
    form = DeleteForm()
    return render_template('previewquiz.html', title=' | Create Class', questions=questions, quiz=quiz, form=form)

@app.route('/quiz/create', methods=['POST'])
@login_required
def createquiz():
    """Renders the create quiz page for educators."""
    if not current_user.check_educator():
        return render_template('error404.html'), 404
    classForm = NameForm(prefix='class')
    quizForm = NameForm(prefix='quiz')
    image_file = url_for('static', filename='resources/images/profile_pics/' + current_user.image_file)
    if quizForm.validate_on_submit():
        quiz = add_quiz(current_user, quizForm.title.data)
        return redirect(url_for('createqn', quizID=quiz.id))
    return render_template('dashboard.html', image_file=image_file, classForm=classForm, quizForm=quizForm)

@app.route('/quiz/<int:quizID>/question', methods=['GET', 'POST'])
@login_required
def createqn(quizID):
    """Renders the add questions page for educators."""
    if not current_user.check_educator():
        return render_template('error404.html'), 404
    quiz = validate_quiz_link(quizID)
    form = QuestionForm()
    if form.validate_on_submit():
        #Commit inputs to database
        options = (form.op1.data, form.op2.data, form.op3.data, form.op4.data)
        question = add_question(form.qn.data, options, form.corrOp.data, form.topic.data)
        add_question_quiz(quiz, question)
        if form.complete.data:
            return redirect(url_for('createquizsuccess', quizID=quizID))
        return redirect(url_for('createqn', quizID=quizID))

    return render_template('createqn.html', title=' | Create Quiz', form=form, quizID=quizID)

@app.route('/quiz/<int:quizID>/question/<int:qnID>/delete', methods=['POST'])
@login_required
def deleteqn(quizID, qnID):
    """Renders the add questions page for educators."""
    if not current_user.check_educator():
        return render_template('error404.html'), 404
    quiz = validate_quiz_link(quizID)
    qn = validate_qn_link(qnID, current_user.id)
    form = DeleteForm()
    if form.validate_on_submit():
        remove_question_quiz(qn, quiz)
        return redirect(url_for('preview_quiz', quizID=quizID))

@app.route('/question/<int:qnID>/edit', methods=['GET', 'POST'])
@login_required
def editqn(qnID):
    """Renders the edit questions page for educators."""
    if not current_user.check_educator():
        return render_template('error404.html'), 404
    qn = validate_qn_link(qnID, current_user.id)
    form = QuestionForm()

    if request.method == 'GET':
        topic = get_topic(qn.topicID)
        topicID = topic.id if topic else 0
        form.topic.data = topicID
        form.qn.data = qn.question
        options = [option.option for option in qn.options]
        form.op1.data, form.op2.data, form.op3.data, form.op4.data = options
        for i in range(len(options)):
            if qn.options[i].id == qn.answerID:
                form.corrOp.data = i + 1
                break

    if form.validate_on_submit():
        #Commit inputs to database
        options = (form.op1.data, form.op2.data, form.op3.data, form.op4.data)
        edit_question(qn, form.qn.data, options, form.corrOp.data, form.topic.data)
        flash('Question Edited Successfully!')
        return redirect(url_for('dashboard'))

    return render_template('createqn.html', title=' | Create Quiz', form=form, edit=True)

@app.route('/quiz/<int:quizID>/success', methods=['GET'])
@login_required
def createquizsuccess(quizID):
    """Renders the create quiz was a success page for educators."""
    return render_template('createquizsuccess.html', title=' | Create Quiz', quizID=quizID)

#@app.route('/class', methods=['GET'])
#def classes():
#    """Renders the class page."""
#    image_file = url_for('static', filename='resources/images/profile_pics/' + current_user.image_file)
#    return render_template('sidebar.html', image_file=image_file, title=' | Class')

@app.route('/class/<int:groupID>/code')
@login_required
def update_class_code(groupID):
    """Routing to update Class Code"""
    group = validate_group_link(groupID)
    if current_user.urole != 'educator':
        return render_template('error404.html'), 404
    set_class_code(group)
    db.session.commit()
    flash('Your class code has been successfully updated!', 'success')
    return redirect(url_for('forum', groupID=groupID))

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    """Renders the contact page."""
    form = ContactForm()
    # POST request
    if request.method == 'POST' and form.validate_on_submit():
        send_contact_email(form)
        return render_template('contact.html', success=True)
    return render_template('contact.html', title=' | Contact Us', form=form)

# Routes for Registration
@app.route('/register')
def reg():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    #Forms for either student or educator
    stuForm = RegistrationForm(prefix='stu')
    eduForm = RegistrationForm(prefix='edu')
    return render_template('register.html', title=' | Register', stuForm=stuForm, eduForm=eduForm)

@app.route('/register/student', methods=['POST'])
def regstu():
    stuForm = RegistrationForm(prefix='stu')
    eduForm = RegistrationForm(prefix='edu')
    if stuForm.validate_on_submit():
        return register(stuForm, 'student')
    return render_template('register.html', title=' | Register', stuForm=stuForm, eduForm=eduForm)

@app.route('/register/educator', methods=['POST'])
def regedu():
    stuForm = RegistrationForm(prefix='stu')
    eduForm = RegistrationForm(prefix='edu')
    if eduForm.validate_on_submit():
        return register(eduForm, 'educator')
    return render_template('register.html', title=' | Register', stuForm=stuForm, eduForm=eduForm)

@app.route('/confirm/<token>')
@login_required
def confirm_email(token):
    try:
        email = confirm_token(token)
    except:
        flash('The confirmation link is invalid or has expired.', 'danger')
        return redirect(url_for('unconfirmed'))
    user = User.query.filter_by(email=email).first_or_404()
    if user.confirmed:
        flash('Account already confirmed. Please login.', 'success')
    else:
        user.confirmed = True
        user.confirmed_on = datetime.datetime.now()
        db.session.add(user)
        db.session.commit()
        flash('You have confirmed your account. Thanks!', 'success')
    return redirect(url_for('home'))

@app.route('/unconfirmed')
@login_required
def unconfirmed():
    if current_user.confirmed:
        return redirect(url_for('home'))
    flash('Please confirm your account!', 'warning')
    return render_template('unconfirmed.html', title=' | Log In')

@app.route('/resend')
@login_required
def resend():
    resend_conf(current_user)
    return redirect(url_for('unconfirmed'))

@app.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user)
        return redirect(url_for('dashboard'))
    return render_template('login.html', title=' | Log In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


# Routes for Class Forum
@app.route('/class/<int:groupID>')
@app.route('/class/<int:groupID>/forum')
#@login_required
def forum(groupID):
    group = validate_group_link(groupID)
    if group is None:
        return redirect(url_for('dashboard'))
    threads = Thread.query.filter_by(groupID=groupID).all()
    image_file = url_for('static', filename='resources/images/profile_pics/' + current_user.image_file)
    return render_template('forum.html', title=' | Forum', groupID=groupID, threads=threads, group=group, image_file=image_file)

@app.route('/class/<int:groupID>/forum/thread/<int:threadID>', methods=['GET', 'POST'])
def forum_post(groupID, threadID):
    # Check validity of link access first
    group = validate_group_link(groupID)
    thread = Thread.query.filter_by(groupID=groupID,id=threadID).first_or_404()

    # Render Posts and PostForm
    posts = Post.query.filter_by(threadID=threadID).all()
    users = get_post_users(posts)

    postForm = PostForm()
    delThreadForm = DeleteForm(prefix="thread")
    delPostForm = DeleteForm(prefix="post")

    # POST request for new post
    if postForm.validate_on_submit():
        save_post(postForm, threadID)
        flash('Your post is now live!')
        return redirect(url_for('forum_post',groupID=groupID,threadID=threadID))
    
    # GET request for forum thread
    return render_template('posts.html', title=' | Forum', thread=thread,posts=posts, postForm=postForm, delThreadForm=delThreadForm, delPostForm=delPostForm, users=users)

@app.route('/class/<int:groupID>/forum/thread/<int:threadID>/delete', methods=['POST'])
def delete_thread(groupID, threadID):
    # Check validity of link access first
    group = validate_group_link(groupID)
    thread = Thread.query.filter_by(groupID=groupID,id=threadID).first_or_404()

    postForm = PostForm()
    delThreadForm = DeleteForm(prefix="thread")
    delPostForm = DeleteForm(prefix="post")

    if delThreadForm.validate_on_submit():

        remove_thread(thread)
        flash('Thread deleted')
        return redirect(url_for('forum', groupID=groupID))

@app.route('/class/<int:groupID>/forum/thread', methods=['GET','POST'])
def create_thread(groupID):
    # Check validity of link access first
    group = validate_group_link(groupID)

    # Render ThreadForm
    form = ThreadForm()

    # POST request for new thread
    if form.validate_on_submit():
        thread = Thread(groupID=groupID, timestamp=datetime.datetime.now(), title=form.title.data)
        db.session.add(thread)
        db.session.commit()
        save_post(form, thread.id)
        flash('Your post is now live!')
        return redirect(url_for('forum_post', groupID=groupID, threadID=thread.id))

    # GET request for create thread
    return render_template('posts.html', title=' | Forum', postForm=form)

@app.route('/class/<int:groupID>/forum/thread/<int:threadID>/delete/<int:postID>', methods=['POST'])
def delete_post(groupID, threadID, postID):
    # Check validity of link access first
    post = validate_post_link(groupID,threadID,postID)
    if post is None:
        return render_template('error404.html'), 404
    postForm = PostForm()
    delThreadForm = DeleteForm(prefix="thread")
    delPostForm = DeleteForm(prefix="post")
    if delPostForm.validate_on_submit():
        db.session.delete(post)
        db.session.commit()
        flash('Post deleted')
        return redirect(url_for('forum_post', groupID=groupID,threadID=threadID))

@app.route('/class/<int:groupID>/forum/thread/<int:threadID>/edit/<int:postID>', methods=['GET','POST'])
def edit_post(groupID,threadID,postID):
    # Check validity of link access first
    post = validate_post_link(groupID,threadID,postID)
    if post is None:
        return render_template('error404.html'), 404

    form = PostForm()
    if request.method == 'GET':
        form.post.data=post.content

    if form.validate_on_submit():
        post.content = form.post.data
        db.session.commit()
        return redirect(url_for('forum_post', groupID=groupID,threadID=threadID))

    return render_template('posts.html', title=' | Forum', postForm=form, editpost=post)

# Routes to delete class
@app.route('/class/<int:groupID>/delete', methods=['GET','POST'])
@login_required
def delete_class(groupID):
     form = DeleteClassForm()
     if form.validate_on_submit():
         group = Group.query.filter_by(id=groupID, classCode = form.title.data).first_or_404()
         remove_group(group)
         flash('Class deleted')
         return redirect(url_for('dashboard'))
     return render_template('deleteclass.html', title=' | Deactivate Account', form=form)


# Routes to edit participants list
@app.route("/class/<int:groupID>/participants")
@login_required
def edit_participants(groupID):
    if not current_user.check_educator():
        return render_template('error404.html'), 404
    group = validate_group_link(groupID)
    users = get_leaderboard(groupID)
    image_file = url_for('static', filename='resources/images/profile_pics/' + current_user.image_file)
    form = DeleteForm()
    return render_template('participants.html', title=' | Edit Participants', image_file=image_file, users=users, group=group, form=form)

@app.route('/class/<int:groupID>/participants/<int:userID>/delete', methods=['POST'])
def delete_participant(groupID, userID):
    form = DeleteForm()
    if not current_user.check_educator():
        return render_template('error404.html'), 404
    group = validate_group_link(groupID)
    user = validate_user_link(groupID, userID)
    if form.validate_on_submit():
        remove_user(group, user)
        flash('User deleted')
        return redirect(url_for('edit_participants',groupID=groupID))
    

# Routes for Quiz
@app.route('/quiz', methods=['GET', 'POST'])
@login_required
def quiz():
    # userID, theta (proficiency), Admistered Items (AI), response vector
    id = current_user.id
    prof, student = get_student_cat(id)

    # If enough questions already attempted, go to result
    if student.stop():
        return redirect(url_for('result'))

    # If attempting the quiz, get the next unanswered question to display
    if request.method == 'GET':
        question, options = get_question_options(student)
        return render_template('quiz.html', question=question, options=options)

    # If submitting an attempted question
    elif request.method == 'POST':
        submit_response(id, request.form)
        return redirect(url_for('quiz'))

@app.route('/quiz/<int:quizID>/<int:qnNum>', methods=['GET','POST'])
@login_required
def edu_quiz(quizID, qnNum):
    quiz = validate_quiz_stu(quizID)
    d = get_question_quiz(quiz, qnNum - 1)

    if len(quiz.questions) < qnNum:
        return redirect(url_for('result', quizID=quizID))

    # If attempting the quiz, get the next unanswered question to display
    if request.method == 'GET':
        question, options = d
        return render_template('quiz.html', quizID=quizID, question=question, options=options)

    # If submitting an attempted question
    elif request.method == 'POST':
        submit_response(id, request.form)
        return redirect(url_for('edu_quiz'),quiz=quiz,qnNum=qnNum+1)

@app.route('/quiz/<int:quizID>/result')
@app.route('/quiz/result')
@login_required
def result(quizID=None):
    quiz = None
    if quizID:
        quiz = validate_quiz_stu(quizID)
    correct, questions = get_response_answer(current_user.id, quizID)
    return render_template('result.html', questions=questions, correct=correct, quiz=quiz)


# Routes to reset password
@app.route("/resetpassword", methods=['GET', 'POST'])
@login_required
def request_reset_password():
     if current_user.is_authenticated:
        return redirect(url_for('quiz'))
     form = ResetPasswordForm()
     if form.validate_on_submit():
         user = User.query.filter_by(email = form.email.data).first()
         send_reset_email(user)
         flash('An email has been sent with instructions to reset your password.', 'info')
         return redirect(url_for('home'))
     return render_template('resetpassword.html', title=' | Reset Password', form=form)

@app.route("/resetpassword/<token>", methods=['GET', 'POST'])
@login_required
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    user = User.verify_reset_token(token)
    if not user:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('request_reset_password'))
    form = NewPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been successfully updated! You can now login with your new password.')
        return redirect(url_for('login'))
    return render_template('changepassword.html', title=' | Reset Password', form = form)


# Routes to deactivate account
@app.route("/deactivate", methods=['GET', 'POST'])
@login_required
def request_deactivate():
     form = DeactivateForm()
     if form.validate_on_submit():
         user = User.query.filter_by(id=current_user.id, email = form.email.data).first_or_404()
         send_deactivate_email(user)
         flash('An email has been sent with instructions to deactivate your account.', 'info')
         return redirect(url_for('request_deactivate'))
     return render_template('deactivate.html', title=' | Deactivate Account', form=form)

@app.route("/deactivate/<token>")
def deactivate_account(token):
    user = User.verify_reset_token(token)
    if not user:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('request_deactivate'))
    else:
        db.session.delete(user)
        db.session.commit()
        flash('Your account has been successfully deactivated! Thank you.')
        return redirect(url_for('home'))
