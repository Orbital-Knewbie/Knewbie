from flask import flash, redirect, url_for
from app import app, db
from app.models import User, Group, Response, Question, Topic
from app.email import get_confirm_url, send_conf_email

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
        

def confirm_user(user):
    '''Confirm a user account'''
    user.confirmed = True
    user.confirmed_on = datetime.now()
    db.session.commit()



def update_image(form_image):
    """To rename & resize image"""
    #rename image
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_image.filename)
    image_filename = random_hex + f_ext
    image_path = os.path.join(app.root_path, 'static/resources/images/profile_pics', image_filename)
    
    # resize image
    img_size = (400, 400)
    new_image = Image.open(form_image)
    new_image.thumbnail(img_size)  
    new_image.save(image_path)
    return image_filename

def set_code(n):
    return ''.join(choice(ascii_letters + digits) for i in range(n))

def set_knewbie_id(user):
    code = set_code(8)
    while User.query.filter_by(knewbie_id=code).first():
        code = set_code(8)
    user.knewbie_id = code
    return user

def get_level_proficiency(user):
    '''Returns a list of proficiency levels for each difficulty range
    Given in the range 0-1 for each difficulty
    [easy_level, med_level, hard_level]'''
    r=Response.query.filter_by(userID=user.id)
    easy = r.filter(Question.difficulty < -1.33).all()
    med = r.filter(Question.difficulty.between(-1.33,1.33)).all()
    hard = r.filter(Question.difficulty > 1.33).all()
    prof_lvl = []
    for diff in (easy,med,hard):
        if not diff:
            prof_lvl.append(0)
        else:
            correct = tuple(filter(lambda x: x.is_correct(), diff))
            prof_lvl.append(correct/len(diff))
    return prof_lvl

def get_topic_proficiencies(user):
    '''Returns a list of proficiency levels for each topic
    Given in the range 0-1 for each topic
    [(topic1, 0.33),(topic2,0.99),...]'''
    r=Response.query.filter_by(userID=user.id)
    prof_lvl = []
    for topic in Topic.query.all():
        curr_prof = r.filter(Question.topicID==topic.id).all()
        if not curr_prof:
            prof_lvl.append((topic.name, 0))
        else:
            correct = tuple(filter(lambda x:x.is_correct(), curr_prof))
            prof_lvl.append((topic.name, correct))
    return prof_lvl

def get_image_file(user):
    image_uri = user.image_file if user.is_authenticated else 'profileimg.jpg'
    return url_for('static', filename='resources/images/profile_pics/' + image_uri)
    