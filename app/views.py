"""
Routes and views for the flask application.
"""

from flask import render_template, request, jsonify, flash, redirect, url_for
from flask_login import current_user, login_user, logout_user, login_required
from app import app, db, mail
from app.models import User, Question, Option, Answer, Response
from app.forms import LoginForm, RegistrationForm, ContactForm, ResetPasswordForm, NewPasswordForm, CreateQnForm, UpdateProfileForm
from app.questions import get_question_options, submit_response
from app.email import register, resend_conf, send_contact_email, send_reset_email
from app.profile import update_image
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
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user)
        return redirect(url_for('dashboard'))
    return render_template('index.html', form=form)

@app.route('/dashboard')
def dashboard():
    """Renders the dashboard page."""
    image_file = url_for('static', filename='resources/images/profile_pics/' + current_user.image_file)
    return render_template('dashboard.html', image_file=image_file)

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    """Renders the settings page."""
    form = UpdateProfileForm()
    if form.validate_on_submit():
        if form.knewbie_id:
            current_user.knewbie_id = current_user.set_knewbie_id()
            db.session.commit()
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

@app.route('/faq')
def faq():
    """Renders the faq page."""
    return render_template('faq.html', title=' | FAQ')

@app.route('/progressreport')
def progressreport():
    """Renders the report page."""
    return render_template('report.html', title=' | Progress Report')

@app.route('/create', methods=['GET', 'POST'])
def create():
    """Renders the create page for educators."""
    form = CreateQnForm()
    return render_template('create.html', title=' | Create', form=form)

#@app.errorhandler(403)
#def page_not_found(e):
#    """Renders the error page."""
#    return render_template('403.html'), 403

#@app.errorhandler(404)
#def page_not_found(e):
#    """Renders the error page."""
#    return render_template('error.html'), 404

#@app.errorhandler(410)
#def page_not_found(e):
#    """Renders the error page."""
#    return render_template('410.html'), 410

#@app.errorhandler(500)
#def page_not_found(e):
#    """Renders the error page."""
#    return render_template('500.html'), 500

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

@app.route('/registerstudent', methods=['POST'])
def regstu():
    stuForm = RegistrationForm(prefix='stu')
    eduForm = RegistrationForm(prefix='edu')
    if stuForm.validate_on_submit():
        return register(stuForm, 'student')
    return render_template('register.html', title=' | Register', stuForm=stuForm, eduForm=eduForm)

@app.route('/registereducator', methods=['POST'])
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


# Routes for Quiz
@app.route('/quiz', methods=['GET', 'POST'])
@login_required
@check_confirmed
def quiz():
    # userID, theta (proficiency), Admistered Items (AI), response vector
    id = current_user.id
    theta = current_user.theta
    AI, responses = current_user.get_AI_responses()
    student = Student(id, theta, AI, responses)

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

@app.route('/result')
@login_required
@check_confirmed
def result():
    AI, responses = current_user.get_AI_responses()

    correct = responses.count(True)
    return '<h1>Correct Answers: <u>' + str(correct) + '/' + str(len(responses)) + '<u></h1>'

# Routes to reset password
@app.route("/resetpassword", methods=['GET', 'POST'])
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
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('quiz'))
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
