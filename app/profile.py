from PIL import Image
from app import app
from string import ascii_letters, digits
from random import choice
import secrets
import os

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

def set_code(self, n):
        return ''.join(choice(ascii_letters + digits) for i in range(n))
        