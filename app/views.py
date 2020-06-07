"""
Routes and views for the flask application.
"""

from flask import render_template, request, jsonify, flash, redirect, url_for
from flask_login import current_user, login_user, logout_user, login_required
from app import app, db, mail
from app.models import User, Question, Option, Answer
from app.forms import LoginForm, RegistrationForm, ContactForm, ResetPasswordForm, NewPasswordForm, CreateQnForm
from app.questions import final_qns
from app.email import register, resend_conf, send_contact_email, send_reset_email
from app.token import confirm_token
from app.decorator import check_confirmed
from flask_mail import Message
import json, datetime

@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
#@login_required
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
    return render_template('index.html', title='Knewbie', form=form)

@app.route('/dashboard')
def dashboard():
    """Renders the dashboard page."""
    return render_template('dashboard.html', title='Knewbie')

@app.route('/settings')
def settings():
    """Renders the dashboard page."""
    return render_template('settings.html', title='Knewbie | Settings')

@app.route('/faq')
def faq():
    """Renders the faq page."""
    return render_template('faq.html', title='Knewbie | FAQ')

@app.route('/create', methods=['GET', 'POST'])
def create():
    """Renders the create page for educators."""
    form = CreateQnForm()
    return render_template('create.html', title='Knewbie | Create', form=form)

@app.route('/error')
def error():
    """Renders the error page."""
    return render_template('error.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    """Renders the contact page."""
    form = ContactForm()
    # POST request
    if request.method == 'POST' and form.validate_on_submit():
        send_contact_email(form)
        return render_template('contact.html', success=True)
    return render_template('contact.html', title='Knewbie | Contact Us', form=form)

@app.route('/register')
def reg():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    #Forms for either student or educator
    stuForm = RegistrationForm(prefix='stu')
    eduForm = RegistrationForm(prefix='edu')
    return render_template('register.html', title='Knewbie | Register', stuForm=stuForm, eduForm=eduForm)

@app.route('/registerstudent', methods=['POST'])
def regstu():
    stuForm = RegistrationForm(prefix='stu')
    eduForm = RegistrationForm(prefix='edu')
    if stuForm.validate_on_submit():
        return register(stuForm, 'student')
    return render_template('register.html', title='Knewbie | Register', stuForm=stuForm, eduForm=eduForm)

@app.route('/registereducator', methods=['POST'])
def regedu():
    stuForm = RegistrationForm(prefix='stu')
    eduForm = RegistrationForm(prefix='edu')
    if eduForm.validate_on_submit():
        return register(eduForm, 'educator')
    return render_template('register.html', title='Knewbie | Register', stuForm=stuForm, eduForm=eduForm)

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
    return render_template('unconfirmed.html', title='Knewbie | Log In')

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
    return render_template('login.html', title='Knewbie | Log In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/quiz')
@login_required
@check_confirmed
def quiz():
    sh_qns, qns = final_qns()
    return render_template('quiz.html', title='Knewbie | Quiz', q = sh_qns, o = qns)

@app.route('/end', methods=['POST'])
def end():
    totalEasy = len(tuple(filter(lambda x: og_qns[x]['difficulty'] == 'Easy', qns.keys())))
    totalHard = len(qns.keys()) - totalEasy
    correct = tuple(filter(lambda x: request.form.get(x) == og_qns[x]['answers'][0], qns.keys()))
    easyCorrect = len(tuple(filter(lambda x: og_qns[x]['difficulty'] == 'Easy', correct)))
    hardCorrect = len(correct) - easyCorrect
    #hardCorrect = tuple(filter(lambda x: og_qns[x]['difficulty'] == 'Easy', correct))
    
    return '<h1>Correct Answers: <u>Easy: ' + str(easyCorrect) + '/' + str(totalEasy) + ' Hard:' + str(hardCorrect) + '/' + str(totalHard) + '<u></h1>'

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
     return render_template('resetpassword.html', title='Knewbie | Reset Password', form=form)

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
    return render_template('changepassword.html', title='Knewbie | Reset Password', form = form)
