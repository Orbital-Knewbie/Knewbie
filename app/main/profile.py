from flask import flash, redirect, url_for
from app import db
from app.models import User, Group, Response, Question, Topic, Proficiency

from PIL import Image
from string import ascii_letters, digits
from random import choice
from datetime import datetime
import secrets, os

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

def get_proficiencies(user):
    '''Return list of (timestamp, proficiency) in chronological order'''
    profs = Proficiency.query.filter_by(userID=user.id,topicID=1). \
        order_by(Proficiency.timestamp.asc()).all()
    return [[prof.timestamp for prof in profs], [prof.theta for prof in profs]]

def get_level_proficiency(user):
    '''Returns a list of proficiency levels for each difficulty range
    Given in the range 0-1 for each difficulty
    [easy_level, med_level, hard_level]'''
    rs=Response.query.filter_by(userID=user.id).all()
    easy = [r for r in rs if r.question.difficulty < -1.33]
    med = [r for r in rs if r.question.difficulty >= -1.33 and r.question.difficulty < 1.33]
    hard = [r for r in rs if r.question.difficulty > 1.33]
    #easy = r.filter(Question.difficulty < -1.33).all()
    #med = r.filter(Question.difficulty.between(-1.33,1.33)).all()
    #hard = r.filter(Question.difficulty > 1.33).all()
    prof_lvl = []
    for diff in (easy,med,hard):
        if not diff:
            prof_lvl.append(0)
        else:
            correct = tuple(filter(lambda x: x.is_correct(), diff))
            prof_lvl.append(len(correct)/len(diff))
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
            prof_lvl.append((topic.name, len(correct)/len(curr_prof)))
    return prof_lvl

def get_image_file(user):
    image_uri = user.image_file if user.is_authenticated else 'profileimg.jpg'
    return url_for('static', filename='resources/images/profile_pics/' + image_uri)
    