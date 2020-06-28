"""
Routes and views for the flask application.
"""

from flask import render_template, request, flash, redirect, url_for, jsonify, make_response
from flask_login import current_user, login_user, logout_user, login_required
from flask_mail import Message
from app import app, db, mail
from app.models import User, Question, Option, Response, Group, Thread, Post, Proficiency, Quiz
from app.forms import *
from app.email import *
from app.profile import *
from app.questions import get_student_cat, submit_response, get_response_answer, get_question, get_all_topics, get_quiz # quiz attempts
from app.questions import add_quiz, add_question, add_question_quiz, get_questions_quiz, edit_question, remove_question_quiz, remove_quiz # quiz making
from app.questions import validate_quiz_link, validate_qn_link, validate_quiz_stu # validation
from app.group import *
from app.forum import *
from app.token import confirm_token
from app.decorator import check_confirmed
from app.cat import Student

import json


# Route for main page functionalities
# home
# progressreport
# faq
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
        #get_data(user)
    diff_prof = get_level_proficiency(user)
    topical_prof = get_topic_proficiencies(user)
    overall_prof = get_proficiencies(user)
    return render_template('report.html', title=' | Progress Report', user=user, diff_prof=diff_prof, topical_prof=topical_prof, overall_prof=overall_prof)

#Get data from database to be used in chart.js
#@app.route('/progressreport/<knewbieID>/get_data')
#def get_data(knewbieID):
#    user = User.query.filter_by(knewbie_id=knewbieID).first()
#    diff_prof = get_level_proficiency(user)
#    topical_prof = get_topic_proficiencies(user)
#    overall_prof = get_proficiencies(user)
#    print(diff_prof, topical_prof, overall_prof)
#    return jsonify({'payload':({'topical_prof':topical_prof, 'diff_prof':diff_prof, 'overall_prof':overall_prof})})

@app.route('/faq')
def faq():
    """Renders the faq page."""
    return render_template('faq.html', title=' | FAQ')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    """Renders the contact page."""
    form = ContactForm()
    # POST request
    if form.validate_on_submit():
        send_contact_email(form)
        return render_template('contact.html', success=True)
    return render_template('contact.html', title=' | Contact Us', form=form)


# Routes for Registration
# register
# confirm
# unconfirmed
# resend
# login
# logout
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
        user = register(stuForm, 'student')
        login_user(user)
        flash('A confirmation email has been sent via email.', 'success')
        return redirect(url_for('unconfirmed'))
    return render_template('register.html', title=' | Register', stuForm=stuForm, eduForm=eduForm)

@app.route('/register/educator', methods=['POST'])
def regedu():
    stuForm = RegistrationForm(prefix='stu')
    eduForm = RegistrationForm(prefix='edu')
    if eduForm.validate_on_submit():
        user = register(eduForm, 'educator')
        login_user(user)
        flash('A confirmation email has been sent via email.', 'success')
        return redirect(url_for('unconfirmed'))
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
        confirm_user(user)
        flash('You have confirmed your account. Thanks!', 'success')
    return redirect(url_for('home'))

@app.route('/unconfirmed')
@login_required
def unconfirmed():
    if current_user.confirmed:
        return redirect(url_for('dashboard'))
    flash('Please confirm your account!', 'warning')
    return render_template('unconfirmed.html', title=' | Log In')

@app.route('/resend')
@login_required
def resend():
    if current_user.confirmed:
        return redirect(url_for('dashboard'))
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


# Route for logged in main page functionalities
# dashboard
# settings
# resetpassword
# deactivate


@app.route('/dashboard')
@login_required
def dashboard():
    """Renders the dashboard page."""
    joinForm = JoinClassForm(prefix='join')
    classForm = NameForm(prefix='class')
    quizForm = NameForm(prefix='quiz')
    image_file = get_image_file(current_user)
    topics = get_all_topics()
    questions = None
    if current_user.check_student():
        correct, questions = get_response_answer(current_user)
    return render_template('dashboard.html', image_file=image_file, classForm=classForm, quizForm=quizForm, joinForm=joinForm, topics=topics, questions=questions)

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
    image_file = get_image_file(current_user)
    return render_template('settings.html', title=' | Settings', image_file=image_file, form=form)

@app.route('/settings/knewbieID')
@login_required
def settings_knewbie_id():
    """Routing to update Knewbie ID"""
    if not current_user.check_student():
        return render_template('errors/error403.html'), 403
    temp = set_code(8)
    while User.query.filter_by(knewbie_id=temp).first() is not None:
        temp = set_code(8)
    db.session.commit()
    flash('Your profile has been successfully updated!', 'success')
    return redirect(url_for('settings'))

# Routes to reset password
@app.route("/resetpassword", methods=['GET', 'POST'])
def request_reset_password():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first_or_404()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('home'))
    return render_template('resetpassword.html', title=' | Reset Password', form=form)

@app.route("/resetpassword/<token>", methods=['GET', 'POST'])
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


# Routes for class
# /class
# join
# create
@app.route('/class/join', methods=['POST'])
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
        return redirect(url_for('forum', groupID=group.id))
    return render_template('dashboard.html', image_file=image_file, classForm=classForm, quizForm=quizForm, joinForm=joinForm)

@app.route('/class/create', methods=['POST'])
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
            return redirect(url_for('dashboard'))
        return redirect(url_for('createclasssuccess', groupID=group.id))
    return render_template('dashboard.html', image_file=image_file, codeForm=codeForm, classForm=classForm, quizForm=quizForm)

# Routes within class
# /class/<int:groupID>
# success
# user
# leaderboard
# delete
# participants
# participants/<int:userID>/delete
@app.route('/class/<int:groupID>/success')
@login_required
def createclasssuccess(groupID):
    """Renders the create class was a success page for educators."""
    if not current_user.check_educator():
        return render_template('errors/error403.html'), 403
    group = validate_group_link(current_user, groupID)
    return render_template('createclasssuccess.html', title=' | Create Class', group=group)


@app.route('/class/<int:groupID>/leaderboard')
@login_required
def leaderboard(groupID):
    """Renders the leaderboard page."""
    group = validate_group_link(current_user, groupID)
    users = get_sorted_students(groupID)
    image_file = get_image_file(current_user)
    return render_template('leaderboard.html', image_file=image_file, title=' | Leaderboard', users=users, group=group)

@app.route('/class/<int:groupID>/code')
@login_required
def update_class_code(groupID):
    """Routing to update Class Code"""
    if not current_user.check_educator():
        return render_template('errors/error403.html'), 403

    group = validate_group_link(current_user, groupID)
    set_class_code(group)
    db.session.commit()
    flash('Your class code has been successfully updated!', 'success')
    return redirect(url_for('forum', groupID=groupID))

# Routes to delete class
@app.route('/class/<int:groupID>/delete', methods=['GET','POST'])
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
        return redirect(url_for('dashboard'))
    return render_template('deleteclass.html', title=' | Deactivate Account', form=form)

@app.route('/class/<int:groupID>/user', methods=['POST'])
@login_required
def adduserclass(groupID):
    """Renders the create class page for educators."""
    if not current_user.check_educator():
        return render_template('errors/error403.html'), 403
    group = validate_group_link(current_user, groupID)
    joinForm = JoinForm()
    deleteForm = DeleteForm()
    if joinForm.validate_on_submit():
        user = User.query.filter_by(knewbie_id=joinForm.title.data).first_or_404()
        if add_user(group, user):
            flash('User added')
        else:
            flash('User already in Class')
        return redirect(url_for('edit_participants', groupID=groupID))

# Routes to edit participants list
@app.route("/class/<int:groupID>/participants")
@login_required
def edit_participants(groupID):
    if not current_user.check_educator():
        return render_template('errors/error403.html'), 403
    group = validate_group_link(current_user, groupID)
    users = get_sorted_students(groupID)
    image_file = get_image_file(current_user)
    joinForm = JoinForm()
    deleteForm = DeleteForm()
    return render_template('participants.html', title=' | Edit Participants', group=group, image_file=image_file, users=users, deleteForm=deleteForm, joinForm=joinForm)

@app.route('/class/<int:groupID>/participants/<int:userID>/delete', methods=['POST'])
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
        return redirect(url_for('edit_participants', groupID=groupID))

# Routes for Class Forum
# forum
# forum/thread
# forum/thread/<int:threadID>
# forum/thread/<int:threadID>/delete
# forum/thread/<int:threadID>/<int:postID>/delete
# forum/thread/<int:threadID>/<int:postID>/edit
@app.route('/class/<int:groupID>')
@app.route('/class/<int:groupID>/forum')
@login_required
def forum(groupID):
    group = validate_group_link(current_user, groupID)
    if group is None:
        return redirect(url_for('dashboard'))
    threads = Thread.query.filter_by(groupID=groupID).all()
    image_file = get_image_file(current_user)
    return render_template('forum.html', title=' | Forum', groupID=groupID, threads=threads, group=group, image_file=image_file)

@app.route('/class/<int:groupID>/forum/thread', methods=['GET','POST'])
@login_required
def create_thread(groupID):
    # Check validity of link access first
    group = validate_group_link(current_user, groupID)

    # Render ThreadForm
    form = ThreadForm()

    # POST request for new thread
    if form.validate_on_submit():
        thread = add_thread(current_user, group, form.title.data, form.content.data)     
        return redirect(url_for('forum_post', groupID=groupID, threadID=thread.id))

    # GET request for create thread
    return render_template('posts.html', title=' | Forum', postForm=form)

@app.route('/class/<int:groupID>/forum/thread/<int:threadID>', methods=['GET', 'POST'])
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
        return redirect(url_for('forum_post',groupID=groupID,threadID=threadID))
    
    # GET request for forum thread
    return render_template('posts.html', title=' | Forum', thread=thread,posts=posts, postForm=postForm, delThreadForm=delThreadForm, delPostForm=delPostForm, users=users)

@app.route('/class/<int:groupID>/forum/thread/<int:threadID>/delete', methods=['POST'])
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
        return redirect(url_for('forum', groupID=groupID))

@app.route('/class/<int:groupID>/forum/thread/<int:threadID>/<int:postID>/delete', methods=['POST'])
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
        return redirect(url_for('forum_post', groupID=groupID,threadID=threadID))

@app.route('/class/<int:groupID>/forum/thread/<int:threadID>/<int:postID>/edit', methods=['GET','POST'])
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
        return redirect(url_for('forum_post', groupID=groupID,threadID=threadID))

    return render_template('posts.html', title=' | Forum', postForm=form, editpost=post)


# Routes for quiz administration
# create
# /<int:quizID>
# success
# question
# question/<int:qnID>/delete
# question/<int:qnID>/edit
@app.route('/quiz/create', methods=['POST'])
@login_required
def createquiz():
    """Renders the create quiz page for educators."""
    if not current_user.check_educator():
        return render_template('errors/error403.html'), 403
    classForm = NameForm(prefix='class')
    quizForm = NameForm(prefix='quiz')
    image_file = get_image_file(current_user)
    if quizForm.validate_on_submit():
        quiz = add_quiz(current_user, quizForm.title.data)
        if quiz is None:
            flash('You have already created a Quiz with this name. Please choose a different name.', 'warning')
            return redirect(url_for('dashboard'))
        return redirect(url_for('createqn', quizID=quiz.id))
    return render_template('dashboard.html', image_file=image_file, classForm=classForm, quizForm=quizForm)

@app.route('/quiz/<int:quizID>/delete', methods=['POST'])
@login_required
def deletequiz(quizID):
    """Renders the create quiz page for educators."""
    if not current_user.check_educator():
        return render_template('errors/error403.html'), 403
    quiz = validate_quiz_link(current_user, quizID)
    delQuizForm = DeleteForm(prefix='quiz')
    delQnForm = DeleteForm(prefix='qn')
    if delQuizForm.validate_on_submit():
        remove_quiz(quiz)
        flash('Quiz deleted')
        return redirect(url_for('dashboard'))


@app.route('/quiz/<int:quizID>/success')
@login_required
def createquizsuccess(quizID):
    """Renders the create quiz was a success page for educators."""
    if not current_user.check_educator():
        return render_template('errors/error403.html'), 403

    return render_template('createquizsuccess.html', title=' | Create Quiz', quizID=quizID)

@app.route('/quiz/<int:quizID>')
@login_required
def preview_quiz(quizID):
    """Renders the preview quiz page for educators."""
    if not current_user.check_educator():
        return render_template('errors/error403.html'), 403
    quiz = validate_quiz_link(current_user, quizID)
    questions = get_questions_quiz(quiz)
    delQuizForm = DeleteForm(prefix='quiz')
    delQnForm = DeleteForm(prefix='qn')
    return render_template('previewquiz.html', title=' | Create Class', questions=questions, quiz=quiz, delQuizForm=delQuizForm, delQnForm=delQnForm)

@app.route('/quiz/<int:quizID>/question', methods=['GET', 'POST'])
@login_required
def createqn(quizID):
    """Renders the add questions page for educators."""
    if not current_user.check_educator():
        return render_template('errors/error403.html'), 403
    quiz = validate_quiz_link(current_user, quizID)
    form = QuestionForm()
    if form.validate_on_submit():
        #Commit inputs to database
        options = (form.op1.data, form.op2.data, form.op3.data, form.op4.data)
        question = add_question(current_user, form.qn.data, options, form.corrOp.data, form.topic.data)
        add_question_quiz(quiz, question)
        flash('Question added')
        if form.complete.data:
            return redirect(url_for('createquizsuccess', quizID=quizID))
        return redirect(url_for('createqn', quizID=quizID))

    return render_template('createqn.html', title=' | Create Quiz', form=form, quizID=quizID)

@app.route('/quiz/<int:quizID>/question/<int:qnID>/delete', methods=['POST'])
@login_required
def deleteqn(quizID, qnID):
    """Renders the add questions page for educators."""
    if not current_user.check_educator():
        return render_template('errors/error403.html'), 403
    quiz = validate_quiz_link(current_user, quizID)
    qn = validate_qn_link(qnID, current_user.id)
    delQuizForm = DeleteForm(prefix='quiz')
    delQnForm = DeleteForm(prefix='qn')
    if delQnForm.validate_on_submit():
        remove_question_quiz(quiz, qn)
        return redirect(url_for('preview_quiz', quizID=quizID))

@app.route('/question/<int:qnID>/edit', methods=['GET', 'POST'])
@login_required
def editqn(qnID):
    """Renders the edit questions page for educators."""
    if not current_user.check_educator():
        return render_template('errors/error403.html'), 403
    qn = validate_qn_link(qnID, current_user.id)
    form = QuestionForm()

    if request.method == 'GET':
        topicID = qn.topicID if qn.topicID else 0
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


# Routes for Quiz attempts
# quiz
# quiz/<int:quizID>/<int:qnNum>
# quiz/result
# quiz/<int:quizID>/result
@app.route('/quiz', methods=['GET', 'POST'])
@login_required
def quiz():
    '''Renders tailored quiz'''
    # Gets a student CAT object for the user
    prof, student = get_student_cat(current_user)

    # If enough questions already attempted, go to result
    if student.stop():
        return redirect(url_for('result'))

    # If attempting the quiz, get the next unanswered question to display
    if request.method == 'GET':
        question, options = student.get_question_options()
        return render_template('quiz.html', question=question, options=options)

    # If submitting an attempted question
    elif request.method == 'POST':
        submit_response(current_user, request.form)
        return redirect(url_for('quiz'))

@app.route('/quiz/<int:quizID>/<int:qnNum>', methods=['GET','POST'])
@login_required
def edu_quiz(quizID, qnNum):
    '''Renders user-created quiz'''
    if not current_user.check_student():
        return render_template('errors/error403.html'), 403
    quiz = validate_quiz_stu(quizID)

    if len(quiz.questions) < qnNum:
        return redirect(url_for('result', quizID=quizID))

    # If attempting the quiz, get the question to display
    if request.method == 'GET':
        question, options = get_question(current_user, quiz, qnNum - 1)
        if question:
            return render_template('quiz.html', quiz=quiz, qnNum=qnNum, question=question, options=options, edu=True)

    # If submitting an attempted question
    elif request.method == 'POST':
        submit_response(current_user, request.form)
    return redirect(url_for('edu_quiz',quizID=quizID,qnNum=qnNum+1))

@app.route('/quiz/<int:quizID>/result')
@app.route('/quiz/result')
@login_required
def result(quizID=None):
    if not current_user.check_student():
        return render_template('errors/error403.html'), 403
    quiz = None
    if quizID:
        quiz = validate_quiz_stu(quizID)
    correct, questions = get_response_answer(current_user, quizID)
    return render_template('result.html', questions=questions, correct=correct, quiz=quiz)

@app.route('/class/<int:groupID>/quizzes')
@login_required
def classquiz(groupID):
    group = validate_group_link(current_user, groupID)
    image_file = get_image_file(current_user)
    quizzes = get_quiz(group)
    return render_template('classquiz.html', title=' | Quiz', group=group, image_file=image_file, quizzes=quizzes)