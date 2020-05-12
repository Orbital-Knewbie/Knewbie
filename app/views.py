"""
Routes and views for the flask application.
"""

from flask import render_template, request, jsonify, flash, redirect, url_for
from flask_login import current_user, login_user, logout_user, login_required
from app import app, db
from random import choice, shuffle
from app.questions import og_qns, qns
from app.forms import LoginForm, RegistrationForm
from app.models import User, Question, Option, Answer
from app.token import generate_confirmation_token, confirm_token
from app.email import send_conf_email
import json, datetime

@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
#@login_required
def home():
    """Renders the home page."""
    return render_template('index.html')

@app.route('/register')
def reg():
    if current_user.is_authenticated:
        return redirect(url_for('quiz'))
     #Forms for either student or educator
    stuForm = RegistrationForm(prefix='stu')
    eduForm = RegistrationForm(prefix='edu')
    return render_template('register.html', stuForm=stuForm, eduForm=eduForm)

@app.route('/registerstudent', methods=['POST'])
def regstu():
    stuForm = RegistrationForm(prefix='stu')
    eduForm = RegistrationForm(prefix='edu')
    if stuForm.validate_on_submit():
        user = User(firstName=stuForm.firstName.data, lastName=stuForm.lastName.data, email=stuForm.email.data, urole='student', confirmed=False)
        user.set_password(stuForm.password.data)
        db.session.add(user)
        db.session.commit()
        token = generate_confirmation_token(user.email)
        confirm_url = url_for('confirm_email', token=token, _external=True)
        html = render_template('email/activate.html', confirm_url=confirm_url)
        subject = "Please confirm your email"
        send_conf_email(user, confirm_url)
        
        #login_user(user)

        flash('A confirmation email has been sent via email.', 'success')
        #flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', stuForm=stuForm, eduForm=eduForm)

@app.route('/registereducator', methods=['POST'])
def regedu():
    stuForm = RegistrationForm(prefix='stu')
    eduForm = RegistrationForm(prefix='edu')
    if eduForm.validate_on_submit():
        user = User(firstName=eduForm.firstName.data, lastName=eduForm.lastName.data, email=eduForm.email.data, urole='educator', confirmed=False)
        user.set_password(eduForm.password.data)
        db.session.add(user)
        db.session.commit()
        token = generate_confirmation_token(user.email)
        confirm_url = url_for('confirm_email', token=token, _external=True)
        html = render_template('email/activate.html', confirm_url=confirm_url)
        subject = "Please confirm your email"
        send_conf_email(user, confirm_url)
                
        #login_user(user)

        flash('A confirmation email has been sent via email.', 'success')
        #flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', stuForm=stuForm, eduForm=eduForm)

@app.route('/confirm/<token>')
@login_required
def confirm_email(token):
    try:
        email = confirm_token(token)
    except:
        flash('The confirmation link is invalid or has expired.', 'danger')
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

@app.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('quiz'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user)
        return redirect(url_for('quiz'))
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/quiz')
def quiz():
    sh_qns = og_qns.keys()
    shuffle(sh_qns)
    for k in qns.keys():
        shuffle(qns[k]['answers'])
    return render_template('quiz.html', q = sh_qns, o = qns)

@app.route('/end', methods=['POST'])
def end():
    totalEasy = len(tuple(filter(lambda x: og_qns[x]['difficulty'] == 'Easy', qns.keys())))
    totalHard = len(qns.keys()) - totalEasy
    correct = tuple(filter(lambda x: request.form.get(x) == og_qns[x]['answers'][0], qns.keys()))
    easyCorrect = len(tuple(filter(lambda x: og_qns[x]['difficulty'] == 'Easy', correct)))
    hardCorrect = len(correct) - easyCorrect
    #hardCorrect = tuple(filter(lambda x: og_qns[x]['difficulty'] == 'Easy', correct))
    
    return '<h1>Correct Answers: <u>Easy: ' + str(easyCorrect) + '/' + str(totalEasy) + ' Hard:' + str(hardCorrect) + '/' + str(totalHard) + '<u></h1>'


@app.route('/test', methods=['GET','POST'])
def test():
    return render_template("test.html")

@app.route('/test1', methods=['GET','POST'])
def test1():
    #data = request.get_json()
    #print(data)
    #easy0 = request.form['Easy']
    #easy1 = request.form['Easy'][1]
    #hard0 = request.form['Hard'][0]
    #hard1 = request.form['Hard'][1]
    #tt=type(easy0)
    #return jsonify({"t1": data, "t2": "yes"})
    test1 = request.form['test1']
    test2 = request.form['test2']
    if test1 == "test1":
        return jsonify({"test1":"works"});