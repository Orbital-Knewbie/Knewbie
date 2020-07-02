from flask import current_app, render_template, url_for, redirect, flash
from flask_mail import Message
from app import db, mail
from app.models import User
from app.auth.token import generate_confirmation_token
from app.email import send_email



def send_conf_email(user, confirm_url):
    send_email('[Knewbie] Confirmation',
               sender=current_app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('email/activate.txt',
                                         name=user.firstName, confirm_url=confirm_url),
               html_body=render_template('email/activate.html',
                                         name=user.firstName, confirm_url=confirm_url))



def send_reset_email(user):
    token = user.reset_token()
    send_email('[Knewbie] Password Reset Request', 
               sender=current_app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('email/reset.txt', name=user.firstName, token=token),
               html_body=render_template('email/reset.html', name=user.firstName, token=token)
    )

def send_deactivate_email(user):
    token = user.reset_token()
    send_email('[Knewbie] Deactivate Account Request', 
               sender=current_app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('email/deactivate.txt', name=user.firstName, token=token),
               html_body=render_template('email/deactivate.html', name=user.firstName, token=token)
    )

def get_confirm_url(user):
    token = generate_confirmation_token(user.email)
    confirm_url = url_for('auth.confirm_email', token=token, _external=True)
    return confirm_url

def resend_conf(user):
    confirm_url = get_confirm_url(user)
    send_conf_email(user, confirm_url)
    flash('A new confirmation email has been sent.', 'success')