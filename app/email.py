from flask_mail import Message
from flask import render_template
from app import app, mail


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