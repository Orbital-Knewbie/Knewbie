
from flask import flash, redirect, url_for
from app import db
from app.models import User, Group, Response, Question, Topic, Proficiency
from app.auth.email import get_confirm_url, send_conf_email
from app.base import set_code

from PIL import Image
from string import ascii_letters, digits
from random import choice
from datetime import datetime
import secrets, os

def register(form, role):
    '''Registers a User given form data'''
    user = User(firstName=form.firstName.data, lastName=form.lastName.data, email=form.email.data, urole=role, confirmed=False)
    user.set_password(form.password.data)
    if role == 'student':
        set_knewbie_id(user)
    db.session.add(user)
    db.session.commit()
    confirm_url = get_confirm_url(user)
    send_conf_email(user, confirm_url)
    return user
        

def confirm_user(user):
    '''Confirm a user account'''
    user.confirmed = True
    user.confirmed_on = datetime.now()
    db.session.commit()

def set_knewbie_id(user):
    code = set_code(8)
    while User.query.filter_by(knewbie_id=code).first():
        code = set_code(8)
    user.knewbie_id = code
    return user