"""
Routes and views for the flask.auth.
"""

from flask import render_template, request, flash, redirect, url_for, jsonify, make_response
from flask_login import current_user, login_user, logout_user, login_required
from app.auth import bp
from app.auth.forms import *
from app.auth.email import *
from app.auth.profile import *
from app.auth.token import confirm_token
from app.decorator import check_confirmed



# Routes for Registration
# register
# confirm
# unconfirmed
# resend
# login
# logout
@bp.route('/register')
def reg():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    #Forms for either student or educator
    stuForm = RegistrationForm(prefix='stu')
    eduForm = RegistrationForm(prefix='edu')
    return render_template('auth/register.html', title=' | Register', stuForm=stuForm, eduForm=eduForm)

@bp.route('/register/student', methods=['POST'])
def regstu():
    stuForm = RegistrationForm(prefix='stu')
    eduForm = RegistrationForm(prefix='edu')
    if stuForm.validate_on_submit():
        user = register(stuForm, 'student')
        login_user(user)
        flash('A confirmation email has been sent via email.', 'success')
        return redirect(url_for('auth.unconfirmed'))
    return render_template('auth/register.html', title=' | Register', stuForm=stuForm, eduForm=eduForm)

@bp.route('/register/educator', methods=['POST'])
def regedu():
    stuForm = RegistrationForm(prefix='stu')
    eduForm = RegistrationForm(prefix='edu')
    if eduForm.validate_on_submit():
        user = register(eduForm, 'educator')
        login_user(user)
        flash('A confirmation email has been sent via email.', 'success')
        return redirect(url_for('auth.unconfirmed'))
    return render_template('auth/register.html', title=' | Register', stuForm=stuForm, eduForm=eduForm)

@bp.route('/confirm/<token>')
@login_required
def confirm_email(token):
    try:
        email = confirm_token(token)
    except:
        flash('The confirmation link is invalid or has expired.', 'danger')
        return redirect(url_for('auth.unconfirmed'))
    user = User.query.filter_by(email=email).first_or_404()
    if user.confirmed:
        flash('Account already confirmed. Please login.', 'success')
    else:
        confirm_user(user)
        flash('You have confirmed your account. Thanks!', 'success')
    return redirect(url_for('main.home'))

@bp.route('/unconfirmed')
@login_required
def unconfirmed():
    if current_user.confirmed:
        return redirect(url_for('main.dashboard'))
    flash('Please confirm your account!', 'warning')
    return render_template('auth/unconfirmed.html', title=' | Log In')

@bp.route('/resend')
@login_required
def resend():
    if current_user.confirmed:
        return redirect(url_for('main.dashboard'))
    resend_conf(current_user)
    return redirect(url_for('auth.unconfirmed'))

@bp.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        login_user(user)
        return redirect(url_for('main.dashboard'))
    return render_template('auth/login.html', title=' | Log In', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))


# Routes to reset password
@bp.route("/resetpassword", methods=['GET', 'POST'])
def request_reset_password():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('main.home'))
    return render_template('auth/resetpassword.html', title=' | Reset Password', form=form)

@bp.route("/resetpassword/<token>", methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    user = User.verify_reset_token(token)
    if not user:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('auth.request_reset_password'))
    form = NewPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been successfully updated! You can now login with your new password.')
        return redirect(url_for('auth.login'))
    return render_template('auth/changepassword.html', title=' | Reset Password', form = form)

# Routes to reset email
@bp.route("/settings/email", methods=['GET', 'POST'])
@login_required
def reset_email():
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        send_new_email(user)
        flash('An email has been sent with instructions to reset your email.', 'info')
        return redirect(url_for('main.settings'))
    return render_template('auth/resetemail.html', title=' | Update Email', form=form)

@bp.route("/resetpassword/<token>", methods=['GET', 'POST'])
@login_required
def new_email(token):
    user = User.verify_reset_token(token)
    if not user:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('auth.reset_email'))
    form = NewEmailForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            flash('Email is the same as the registered email. Please use a different email address.')
        else:
            current_user.email = form.email.data
            db.session.commit()
            flash('Your email has been successfully updated! You can now login with your new email.')
        return redirect(url_for('main.settings'))
    return render_template('auth/newemail.html', title=' | Update Email', form = form)

# Routes to deactivate account
@bp.route("/deactivate", methods=['GET', 'POST'])
@login_required
def request_deactivate():
     form = DeactivateForm()
     if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.request_deactivate'))
        send_deactivate_email(user)
        flash('An email has been sent with instructions to deactivate your account.', 'info')
        return redirect(url_for('auth.request_deactivate'))
     return render_template('auth/deactivate.html', title=' | Deactivate Account', form=form)

@bp.route("/deactivate/<token>")
def deactivate_account(token):
    user = User.verify_reset_token(token)
    if not user:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('auth.request_deactivate'))
    else:
        db.session.delete(user)
        db.session.commit()
        flash('Your account has been successfully deactivated! Thank you.')
        return redirect(url_for('main.home'))
