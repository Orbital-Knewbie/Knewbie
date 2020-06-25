from flask import flash, redirect, url_for
from flask_login import login_user
from app import app, db
from app.models import User, Group
from app.email import get_confirm_url, send_conf_email

from PIL import Image
from string import ascii_letters, digits
from random import choice
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
        
    login_user(user)

    flash('A confirmation email has been sent via email.', 'success')
    return redirect(url_for('unconfirmed'))

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