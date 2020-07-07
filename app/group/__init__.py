from flask import Blueprint

bp = Blueprint('group', __name__)

from app.group import views
