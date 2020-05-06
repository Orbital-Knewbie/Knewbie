"""
Routes and views for the flask application.
"""

from flask import render_template
from app import app

qns = {
    "Fill in the blank: 423 x 1000 = ____ x 10": [423, 4230, 42300, 423000],
    "Which of the following is closest to 1?": ["1/2", "2/3", "3/4", "4/5"],
    "Which of the following is the same as 2010 g?": ["2 kg 1 g", "2 kg 10 g", "20 kg 1 g", "20 kg 10 g"]
}

@app.route('/')
@app.route('/home')
def home():
    """Renders the home page."""
    return render_template('index.html')