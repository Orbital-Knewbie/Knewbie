"""
Routes and views for the flask application.
"""

from flask import render_template, request
from app import app
from random import choice, shuffle
from app.questions import *

@app.route('/')
@app.route('/home')
def home():
    """Renders the home page."""
    return render_template('index.html')

@app.route('/quiz')
def quiz():
    sh_qns = og_qns.keys()
    shuffle(sh_qns)
    for k in qns.keys():
        shuffle(qns[k])
    return render_template('quiz.html', q = sh_qns, o = qns)

@app.route('/end', methods=['POST'])
def end():
    correct = len(filter(lambda x: request.form[x] == og_qns[x][0], qns.keys()))
    #for q in questions.keys():
    #    ans = request.form[q]
    #    if ans == og_qns[q][0]:
    #        correct += 1
    return '<h1>Correct Answers: <u>' + str(correct) + '</u></h1>'