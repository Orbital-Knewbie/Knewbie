"""
Routes and views for the flask application.
"""

from flask import render_template, request, jsonify
from app import app
from random import choice, shuffle
from app.questions import *
import json

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
    return '<h1>Correct Answers: <u>' + str(correct) + '</u></h1>'

@app.route('/test', methods=['GET','POST'])
def test():
    return render_template("test.html")

@app.route('/test1', methods=['GET','POST'])
def test1():
    #data = request.get_json()
    #print(data)
    #easy0 = request.form['Easy']
    #easy1 = request.form['Easy'][1]
    #hard0 = request.form['Hard'][0]
    #hard1 = request.form['Hard'][1]
    #tt=type(easy0)
    #return jsonify({"t1": data, "t2": "yes"})
    test1 = request.form['test1']
    test2 = request.form['test2']
    if test1 == "test1":
        return jsonify({"test1":"works"});