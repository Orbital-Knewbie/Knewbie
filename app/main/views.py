"""
Routes and views for the flask application.
"""

from flask import render_template, request, flash, redirect, url_for, jsonify, make_response
from flask_login import current_user, login_user, logout_user, login_required
from flask_mail import Message
from app import db, mail
from app.main import bp
from app.models import *
from app.main.forms import *
from app.main.profile import *
from app.main.email import *
from app.auth.email import get_confirm_url, send_conf_email
from app.decorator import check_confirmed

import json


# Route for main page functionalities
# home
# progressreport
# faq
@bp.route('/', methods=['GET', 'POST'])
@bp.route('/home', methods=['GET', 'POST'])
def home():
    """Renders the home page."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    loginForm = LoginForm(prefix='login')
    codeForm = CodeForm(prefix='code')
    if loginForm.validate_on_submit():
        user = User.query.filter_by(email=loginForm.email.data).first()
        if user is None or not user.check_password(loginForm.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        login_user(user)
        return redirect(url_for('main.dashboard'))

    return render_template('index.html', loginForm=loginForm, codeForm=codeForm)

@bp.route('/progressreport', methods=['GET', 'POST'])
def get_report():
    """Renders the report page."""
    loginForm = LoginForm(prefix='login')
    codeForm = CodeForm(prefix='code')
    if request.method == 'GET':
        return redirect(url_for('main.progressreport'))
    if codeForm.validate_on_submit():
        return redirect(url_for('main.progressreport',knewbieID=codeForm.title.data))

@bp.route('/progressreport/')
@bp.route('/progressreport/<knewbieID>')
def progressreport(knewbieID=None):
    if knewbieID is None:
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        elif current_user.urole == 'educator':
            return redirect(url_for('main.dashboard'))
        user = current_user
    else:
        user = User.query.filter_by(knewbie_id=knewbieID).first_or_404()
        #get_data(user)
    diff_prof = get_level_proficiency(user)
    topical_prof = get_topic_proficiencies(user)
    overall_prof = get_proficiencies(user)
    return render_template('report.html', title=' | Progress Report', user=user, diff_prof=diff_prof, topical_prof=topical_prof, overall_prof=overall_prof)

#Get data from database to be used in chart.js
#@bp.route('/progressreport/<knewbieID>/get_data')
#def get_data(knewbieID):
#    user = User.query.filter_by(knewbie_id=knewbieID).first()
#    diff_prof = get_level_proficiency(user)
#    topical_prof = get_topic_proficiencies(user)
#    overall_prof = get_proficiencies(user)
#    print(diff_prof, topical_prof, overall_prof)
#    return jsonify({'payload':({'topical_prof':topical_prof, 'diff_prof':diff_prof, 'overall_prof':overall_prof})})

@bp.route('/faq')
def faq():
    """Renders the faq page."""
    return render_template('faq.html', title=' | FAQ')

@bp.route('/contact', methods=['GET', 'POST'])
def contact():
    """Renders the contact page."""
    form = ContactForm()
    # POST request
    if form.validate_on_submit():
        send_contact_email(form)
        return render_template('contact.html', success=True)
    return render_template('contact.html', title=' | Contact Us', form=form)


# Route for logged in main page functionalities
# dashboard
# settings

@bp.route('/dashboard')
@login_required
def dashboard():
    """Renders the dashboard page."""
    joinForm = JoinClassForm(prefix='join')
    classForm = NameForm(prefix='class')
    quizForm = NameForm(prefix='quiz')
    image_file = get_image_file(current_user)
    topics = Topic.query.all()
    respond = Response.query.filter_by(userID=current_user.id).filter(Question.user.has(admin=True)).all()
    return render_template('dashboard.html', image_file=image_file, classForm=classForm, quizForm=quizForm, joinForm=joinForm, topics=topics, respond=respond)

@bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """Renders the settings page."""
    form = UpdateProfileForm(prefix='profile')
    knewbieForm = ChangeKnewbieForm(prefix='knewbie')
    pwForm = UpdatePasswordForm(prefix='pw')
    emailForm = UpdateEmailForm(prefix='email')

    if form.validate_on_submit():            
        if form.image.data:
            image_file = update_image(form.image.data)
            current_user.image_file = image_file
        current_user.firstName = form.firstName.data
        current_user.lastName = form.lastName.data
        db.session.commit()
        flash('Your profile has been successfully updated!', 'success')
        return redirect(url_for('main.settings'))
    elif request.method == 'GET':
        form.firstName.data = current_user.firstName
        form.lastName.data = current_user.lastName
    image_file = get_image_file(current_user)
    return render_template('settings.html', title=' | Settings', image_file=image_file, form=form, knewbieForm=knewbieForm, pwForm=pwForm, emailForm=emailForm)

@bp.route('/settings/knewbieID', methods=['POST'])
@login_required
def settings_knewbie_id():
    """Routing to update Knewbie ID"""
    
    if not current_user.check_student():
        return render_template('errors/error403.html'), 403
    form = UpdateProfileForm(prefix='profile')
    knewbieForm = ChangeKnewbieForm(prefix='knewbie')
    if knewbieForm.validate_on_submit():
        set_knewbie_id(current_user)
        db.session.commit()
        flash('Your profile has been successfully updated!', 'success')
    return redirect(url_for('main.settings'))

@bp.route('/settings/email', methods=['POST'])
@login_required
def change_email():
    """Routing to change email from settings"""   
    form = UpdateProfileForm(prefix='profile')
    knewbieForm = ChangeKnewbieForm(prefix='knewbie')
    pwForm = UpdatePasswordForm(prefix='pw')
    emailForm = UpdateEmailForm(prefix='email')

    if emailForm.validate_on_submit():
        user = User.query.filter_by(email=emailForm.email.data).first()
        if user is None:
            current_user.email = emailForm.email.data
            confirm_url = get_confirm_url(current_user)
            send_conf_email(current_user, confirm_url)
            db.session.commit()
            flash('A confirmation email has been sent via email. Please verify for the change to take place.', 'success')
            return redirect(url_for('auth.unconfirmed'))
        elif user is not None:
            flash('Enter a new email address if you want to update it, otherwise leave the fields blank!')
            return redirect(url_for('main.settings'))

@bp.route('/settings/password', methods=['POST'])
@login_required
def change_pw():
    """Routing to change PW from settings"""
    form = UpdateProfileForm(prefix='profile')
    knewbieForm = ChangeKnewbieForm(prefix='knewbie')
    pwForm = UpdatePasswordForm(prefix='pw')
    emailForm = UpdateEmailForm(prefix='email')
    
    if pwForm.validate_on_submit():
        if not current_user.check_password(pwForm.password.data):
            flash('Invalid current password, please try again')
        elif current_user.check_password(pwForm.newPassword.data):
            flash('You cannot reuse your old password. Please choose a different password.', 'success')
        else:
            current_user.set_password(pwForm.confirmPassword.data)
            db.session.commit()
            flash('Your profile has been successfully updated!', 'success')
    image_file = get_image_file(current_user)
    return render_template('settings.html', title=' | Settings', image_file=image_file, form=form, knewbieForm=knewbieForm, pwForm=pwForm, emailForm=emailForm)
