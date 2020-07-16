"""
Routes and views for the flask application.
"""

from flask import render_template, request, flash, redirect, url_for, jsonify, make_response
from flask_login import current_user, login_user, logout_user, login_required
from flask_mail import Message
from app import db, mail
from app.quiz import bp
from app.models import User, Question, Option, Response, Group, Thread, Post, Proficiency, Quiz
from app.quiz.forms import *
from app.base import *
from app.quiz.questions import *
from app.decorator import check_confirmed



# Routes for quiz administration
# create
# /<int:quizID>
# success
# question
# question/<int:qnID>/delete
# question/<int:qnID>/edit
@bp.route('/create', methods=['POST'])
@login_required
def createquiz():
    """Renders the create quiz page for educators."""
    if not current_user.check_educator():
        return render_template('errors/error403.html'), 403
    classForm = NameForm(prefix='class')
    quizForm = NameForm(prefix='quiz')
    image_file = get_image_file(current_user)
    if quizForm.validate_on_submit():
        quiz = add_quiz(current_user, quizForm.title.data)
        if quiz is None:
            flash('You have already created a Quiz with this name. Please choose a different name.', 'warning')
            return redirect(url_for('main.dashboard'))
        return redirect(url_for('quiz.createqn', quizID=quiz.id))
    return render_template('dashboard.html', image_file=image_file, classForm=classForm, quizForm=quizForm)

@bp.route('/<int:quizID>/delete', methods=['POST'])
@login_required
def deletequiz(quizID):
    """Renders the create quiz page for educators."""
    if not current_user.check_educator():
        return render_template('errors/error403.html'), 403
    quiz = validate_quiz_link(current_user, quizID)
    delQuizForm = DeleteForm(prefix='quiz')
    delQnForm = DeleteForm(prefix='qn')
    if delQuizForm.validate_on_submit():
        remove_quiz(quiz)
        flash('Quiz deleted')
        return redirect(url_for('main.dashboard'))


@bp.route('/<int:quizID>/success')
@login_required
def createquizsuccess(quizID):
    """Renders the create quiz was a success page for educators."""
    if not current_user.check_educator():
        return render_template('errors/error403.html'), 403

    return render_template('quiz/createquizsuccess.html', title=' | Create Quiz', quizID=quizID)

@bp.route('/<int:quizID>')
@login_required
def preview_quiz(quizID):
    """Renders the preview quiz page for educators."""
    if not current_user.check_educator():
        return render_template('errors/error403.html'), 403
    quiz = validate_quiz_link(current_user, quizID)
    questions = get_questions_quiz(quiz)
    image_file = get_qn_image(questions)
    delQuizForm = DeleteForm(prefix='quiz')
    delQnForm = DeleteForm(prefix='qn')
    return render_template('quiz/previewquiz.html', title=' | Create Class', questions=questions, quiz=quiz, delQuizForm=delQuizForm, delQnForm=delQnForm, image_file=image_file)

@bp.route('/<int:quizID>/question', methods=['GET', 'POST'])
@login_required
def createqn(quizID):
    """Renders the add questions page for educators."""
    if not current_user.check_educator():
        return render_template('errors/error403.html'), 403
    quiz = validate_quiz_link(current_user, quizID)
    form = QuestionForm()
    delQuizForm = DeleteForm(prefix='quiz')
    delQnForm = DeleteForm(prefix='qn')
    if form.validate_on_submit():
        #Commit inputs to database
        options = (form.op1.data, form.op2.data, form.op3.data, form.op4.data)
        question = add_question(current_user, form.qn.data, options, form.corrOp.data, form.topic.data)
        if form.img.data:
            quiz.image_file = update_qn_image(form.img.data)
        add_question_quiz(quiz, question)
        flash('Question added')
        if form.complete.data:
            return redirect(url_for('quiz.createquizsuccess', quizID=quizID))
        return redirect(url_for('quiz.createqn', quizID=quizID))

    return render_template('quiz/createqn.html', title=' | Create Quiz', form=form, quiz=quiz,delQuizForm=delQuizForm, delQnForm=delQnForm, image_file=image_file)

@bp.route('/<int:quizID>/question/<int:qnID>/delete', methods=['POST'])
@login_required
def deleteqn(quizID, qnID):
    """Routing to delete a question from a quiz for educators."""
    if not current_user.check_educator():
        return render_template('errors/error403.html'), 403
    quiz = validate_quiz_link(current_user, quizID)
    qn = validate_qn_link(qnID, current_user.id)
    delQuizForm = DeleteForm(prefix='quiz')
    delQnForm = DeleteForm(prefix='qn')
    if delQnForm.validate_on_submit():
        remove_question_quiz(quiz, qn)
        flash('Question removed from Quiz')
        return redirect(url_for('quiz.preview_quiz', quizID=quizID))

@bp.route('/question/<int:qnID>/edit', methods=['GET', 'POST'])
@login_required
def editqn(qnID):
    """Renders the edit questions page for educators."""
    if not current_user.check_educator():
        return render_template('errors/error403.html'), 403
    qn = validate_qn_link(qnID, current_user.id)
    form = QuestionForm()

    if request.method == 'GET':
        topicID = qn.topicID if qn.topicID else 0
        form.topic.data = topicID
        form.qn.data = qn.question
        options = [option.option for option in qn.options]
        form.op1.data, form.op2.data, form.op3.data, form.op4.data = options
        for i in range(len(options)):
            if qn.options[i].id == qn.answerID:
                form.corrOp.data = i + 1
                break

    if form.validate_on_submit():
        #Commit inputs to database
        options = (form.op1.data, form.op2.data, form.op3.data, form.op4.data)
        edit_question(qn, form.qn.data, options, form.corrOp.data, form.topic.data)
        flash('Question Edited Successfully!')
        return redirect(url_for('main.dashboard'))

    return render_template('quiz/createqn.html', title=' | Create Quiz', form=form, edit=True)


# Routes for Quiz attempts
# quiz
# quiz/<int:quizID>/<int:qnNum>
# quiz/result
# quiz/<int:quizID>/result
@bp.route('/tailored/', methods=['GET', 'POST'])
@bp.route('/tailored/<int:attempt>', methods=['GET', 'POST'])
@login_required
def quiz(attempt=None):
    '''Renders tailored quiz'''
    # Gets a student CAT object for the user
    prof, student = get_student_cat(current_user, 1, attempt)

    # If enough questions already attempted, go to result
    if student.stop():
        return redirect(url_for('quiz.result'))

    # If attempting the quiz, get the next unanswered question to display
    if request.method == 'GET':
        question, options = student.get_question_options()
        if question is None:
            return redirect(url_for('quiz.result'))
        return render_template('quiz/quiz.html', question=question, options=options, attempt=attempt)

    # If submitting an attempted question
    elif request.method == 'POST':
        submit_response(current_user, request.form)
        return redirect(url_for('quiz.quiz',attempt=attempt))

### UNTESTED
@bp.route('/tailored/reattempt', methods=['POST'])
@login_required
def reattempt():
    '''Reattempt tailored quiz'''
    if not current_user.check_student():
        return render_template('errors/error403.html'), 403

    form = ReattemptForm()
    if form.validate_on_submit():
        remove_incorrect_responses(current_user)
        correct, questions = get_response_answer(current_user)   

        return redirect(url_for('quiz.quiz', attempt=correct+4))

    return redirect(url_for('main.dashboard'))

@bp.route('/<int:quizID>/<int:qnNum>', methods=['GET','POST'])
@login_required
def edu_quiz(quizID, qnNum):
    '''Renders user-created quiz'''
    if not current_user.check_student():
        return render_template('errors/error403.html'), 403
    quiz = validate_quiz_stu(quizID)

    if len(quiz.questions) < qnNum:
        return redirect(url_for('quiz.result', quizID=quizID))

    # If attempting the quiz, get the question to display
    if request.method == 'GET':
        question, options = get_question(current_user, quiz, qnNum - 1)
        if question:
            return render_template('quiz/quiz.html', quiz=quiz, qnNum=qnNum, question=question, options=options, edu=True)

    # If submitting an attempted question
    elif request.method == 'POST':
        submit_response(current_user, request.form)
    return redirect(url_for('quiz.edu_quiz',quizID=quizID,qnNum=qnNum+1))

### UNTESTED
@bp.route('/<int:quizID>/reattempt', methods=['POST'])
@login_required
def reattempt_edu(quizID):
    '''Reattempt educator quiz'''
    if not current_user.check_student():
        return render_template('errors/error403.html'), 403
    quiz = validate_quiz_stu_edu(current_user, quizID)

    form = ReattemptForm()
    if form.validate_on_submit():
        remove_quiz_responses(current_user, quiz)

    return redirect(url_for('quiz.edu_quiz', quizID=quizID, qnNum=1))

@bp.route('/<int:quizID>/result')
@bp.route('/result')
@login_required
def result(quizID=None):
    if not current_user.check_student():
        return render_template('errors/error403.html'), 403
    form = ReattemptForm()
    quiz = None
    if quizID:
        quiz = validate_quiz_stu(quizID)
    correct, questions = get_response_answer(current_user, quizID)
    return render_template('quiz/result.html', questions=questions, correct=correct, quiz=quiz, form=form)

