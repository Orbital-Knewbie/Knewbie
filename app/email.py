from flask import render_template, url_for, redirect, flash
from flask_mail import Message
from flask_login import login_user
from app import app, db, mail
from app.models import User
from app.token import generate_confirmation_token


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)

def send_conf_email(user, confirm_url):
    send_email('[Knewbie] Confirmation',
               sender=app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('email/activate.txt',
                                         name=user.firstName, confirm_url=confirm_url),
               html_body=render_template('email/activate.html',
                                         name=user.firstName, confirm_url=confirm_url))

def get_confirm_url(user):
    token = generate_confirmation_token(user.email)
    confirm_url = url_for('confirm_email', token=token, _external=True)
    return confirm_url

def register(form, role):
    user = User(firstName=form.firstName.data, lastName=form.lastName.data, email=form.email.data, urole=role, confirmed=False)
    user.set_password(form.password.data)
    db.session.add(user)
    db.session.commit()
    confirm_url = get_confirm_url(user)
    send_conf_email(user, confirm_url)
        
    #login_user(user)

    flash('A confirmation email has been sent via email.', 'success')
    #flash('Congratulations, you are now a registered user!')
    return redirect(url_for('unconfirmed'))

def resend_conf(user):
    confirm_url = get_confirm_url(user)
    send_conf_email(user, confirm_url)
    flash('A new confirmation email has been sent.', 'success')