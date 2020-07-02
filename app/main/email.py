from flask import current_app, render_template, url_for, redirect, flash
from flask_mail import Message
from app import db, mail
from app.email import send_email


def send_contact_email(form):
    send_email('[Knewbie] Contact',
               sender=current_app.config['ADMINS'][0],
               recipients=current_app.config['ADMINS'],
               text_body=render_template('email/contactmsg.txt', form=form),
               html_body=render_template('email/contactmsg.html', form=form)
    )