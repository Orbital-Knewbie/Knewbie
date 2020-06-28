from app import db
from app.models import Question, Option, Response, Proficiency, Topic, Group, User, Quiz
from app.cat import Student

# this function generates an item bank, in case the user cannot provide one
from catsim.cat import generate_item_bank

from random import choice, shuffle
from datetime import datetime

import glob, os, json


def add_qn(org_qns):
    '''Adds questions to the database, where questions are formatted to be in a dictionary
    {<question>:{'answer':<options>,'difficulty':<difficulty>}
    <questions> is str
    <options> is list of str
    <difficulty> is float (not added yet)
    '''
    if Question.query.all(): return
    for q in org_qns.keys():
        item = generate_item_bank(1)[0]
        qn = Question(question=q, discrimination=item[0], \
                    difficulty=item[1], guessing=item[2], upper=item[3], topicID=1)
        db.session.add(qn)
        db.session.commit()
        qid = qn.id
        b=True
        for o in org_qns[q]['answers']:
            opt=Option(qnID=qid,option=o)
            db.session.add(opt)
            if b:
                db.session.flush()
                qn.answerID = opt.id
                
                b=False
            
            db.session.commit()


def insert_qns(path):
    '''Inserts questions formatted as a json file
    {<number>:
    {'answer':<extra text><answer>,
    'option_texts':<extra text><options>, 
    'question_text':<extra text><question><extra text>}}
    all are strings
    '''
    qn_dict = {}
    for filename in glob.glob(os.path.join(path, '*.json')):
        print("===")
        print(filename)
        print("===")
        with open(filename, 'r') as f: # open in readonly mode
            data = json.load(f)
            for qn_set in data.values():
                qn_txt = qn_set["question_text"]
                n, qn_text = qn_txt.split(")",1)
                options = qn_set["option_texts"]
                options = [[o[0], o[6:]] for o in options]
                
                answer = qn_set["answer"]
                a, answer = answer.split("Answer / Explanation :\n\nAnswer : ", 1)
                answer, explanation = answer.split(".", 1)

                item = generate_item_bank(1)[0]

                question = Question(question=qn_text, discrimination=item[0], \
                    difficulty=item[1], guessing=item[2], upper=item[3], topicID=1)
                db.session.add(question)
                db.session.flush()
                qid = question.id

                for opt in options:
                    o = Option(qnID=qid, option=opt[1])
                    db.session.add(o)
                    if opt[0] == answer:
                        db.session.flush()
                        optID = o.id
                        question.answerID = optID

                db.session.commit()

def get_student_cat(user, topicID=1):
    '''Returns proficiency, student (CAT object) given a userID and optional topicID
    Defaults to overall proficiency (topicID=1)'''

    prof = Proficiency.query.filter_by(userID=user.id,topicID=topicID)
    if not prof.all():
        prof = create_student_prof(user)
    else:
        prof = prof.order_by(Proficiency.timestamp.desc()).first()
    AI, responses = prof.get_AI_responses()

    student = Student(user.id, topicID, prof.theta, AI, responses)
    return prof, student

def submit_response(user, form):
    '''Submit Question Response to Database'''
    # Get the submitted Option
    optID = form.get('option')
    option = Option.query.filter_by(id=optID).first()
    qnID = option.qnID

    # Create a Response entry
    response = Response(userID=user.id,optID=option.id,qnID=option.qnID)

    # Save to DB
    db.session.add(response)
    db.session.commit()

    # Update topic / overall proficiency
    qn = Question.query.filter_by(id=qnID).first()
    topicID = qn.topicID if qn.topicID else 1
    if topicID > 1:
        update_proficiency(user, topicID)
    update_proficiency(user)

def update_proficiency(user, topicID=1):
    '''Updates user proficiency given a topic'''
    prof, topic_student = get_student_cat(user, topicID)
    topic_student.update()
    prof.theta = topic_student.theta
    if topicID == 1:
        user.curr_theta = topic_student.theta
    db.session.commit()

def add_proficiency(user):
    '''Add timestamped proficiency entity, done every completed quiz'''
    prof, student = get_student_cat(user)
    new_prof = Proficiency(userID=user.id, timestamp=datetime.now(), 
                           theta=student.theta, topicID=1)
    db.session.add(new_prof)
    db.session.commit()

def create_student_prof(user):
    '''Creates a proficiency entity for a student'''
    if not Topic.query.all():
        add_topic("first")
    topics = db.session.query(Topic.id).all()

    # Initialize CAT random theta for student 
    student_cat = Student(user.id)
    user.curr_theta = student_cat.theta

    overall_prof = None
    # Add a Proficiency for each topic in the database
    for topic, in topics:            
        prof = Proficiency(userID=user.id, timestamp=datetime.now(), 
                           theta=student_cat.theta, topicID=topic)
        db.session.add(prof)
        if overall_prof is None:
            overall_prof = prof
    db.session.commit()
    return overall_prof

def get_all_topics():
    return Topic.query.all()

def get_topic(topicID):
    return Topic.query.filter_by(id=topicID).first()

def add_question(user, qn_text, options, answer, topicID):
    '''Adds a question to the database
    Input
    qn_text : str
    options : seq of str
    answer : int (1 to 4)
    topic : int
    '''
    # Generate item parameters from CatSim
    item = generate_item_bank(1)[0]

    # Add question
    question = Question(question=qn_text, discrimination=item[0], \
        difficulty=item[1], guessing=item[2], upper=item[3], topicID = topicID, userID=user.id)
    db.session.add(question)
    db.session.flush()

    qnID = question.id
    
    # Add options and answer
    for opt in options:
        o = Option(qnID=qnID,option=opt)
        answer -= 1
        db.session.add(o)
        db.session.flush()
        if answer == 0:
            optID = o.id
            question.answerID = optID
            db.session.flush()
    db.session.commit()
    return question

def edit_question(question, qn_text, options, answer, topicID):
    question.question = qn_text
    question.topicID = topicID
    for i in range(len(options)):
        curr_option = question.options[i]
        curr_option.option = options[i]
        if answer == i + 1:
            question.answerID = curr_option.id
    db.session.commit()
    return question


def get_response_answer(user, quizID=None):
    '''Given userID, optional quizID
    Returns number of correct responses, 
    and dictionary with format
    {question_txt : [[opt1_txt,...], ans_num, res_num], ...}
    ans_num and res_num given as int 1-4
    '''
    if quizID is None:
        responses = Response.query.filter_by(userID=user.id).filter(Question.user.has(admin=True)).all()
    else:
        responses = Response.query.filter_by(userID=user.id).filter(Question.quizzes.any(id=quizID)).all()
    d={}
    correct = 0
    for r in responses:
        qnID = r.qnID
        qn = Question.query.filter_by(id=qnID).first()
        qn_txt = qn.question
        opt = Option.query.filter_by(qnID=qnID).all()
        opt_txt = []
        #ans = Answer.query.filter_by(qnID=qnID).first().optID
        ans = qn.answerID
        for i in range(len(opt)):
            opt_txt.append(opt[i].option)
            if opt[i].id == ans:
                ans_num = i
            if opt[i].id == r.optID:
                res_num = i
        if ans_num == res_num:
            correct += 1
        d[qn_txt]=[opt_txt,ans_num,res_num]

    return correct, d

def add_quiz(user, name):
    '''Adds educator created quiz'''
    if Quiz.query.filter_by(userID=user.id, name=name).first():
        return
    quiz = Quiz(userID=user.id, name=name)
    db.session.add(quiz)
    db.session.commit()
    return quiz

def remove_quiz(quiz):
    quiz.questions = []
    db.session.delete(quiz)
    db.session.commit()

def add_question_quiz(quiz, question):
    '''Adds a question to an educator created quiz'''
    if question in quiz.questions: return
    quiz.questions.append(question)
    db.session.commit()

def remove_question_quiz(quiz, question):
    '''Removes a question from a quiz (not database)'''
    quiz.questions.remove(question)
    db.session.commit()

def remove_question(question):
    '''Removes a question and its options from the database'''
    options = question.options
    responses = question.responses
    question.quizzes = []
    db.session.delete(question)
    for o in options:
        db.session.delete(o)
    for r in responses:
        db.session.delete(r)
    db.session.commit()

def add_quiz_group(group, quiz):
    '''Adds a quiz to a class'''
    if quiz in group.quizzes: return
    group.quizzes.append(quiz)
    db.session.commit()

def get_quiz(group):
    return Quiz.query.filter(Quiz.groups.any(id=group.id)).all()

def get_questions_quiz(quiz, pre_shuffle=False):
    '''Gets dictionary of questions belonging to a quiz
    Format - 
    {question_txt :
        {
            {options :
                {optionID : option_txt, 
                ...}
            ,
            answer : optionID}
        },
    ...
    }
    '''
    d = {}
    questions = quiz.questions
    for question in questions:
        qnID = question.id
        qn_txt = question.question
        options = question.options
        if pre_shuffle:
            shuffle(options)
        opt_txt = {option.id : option.option for option in options}
        d[qnID] = {'question' : qn_txt, 'options' : opt_txt, 'answer' : question.answerID}
    return d

def get_question(user, quiz, n, pre_shuffle=False):
    '''Gets nth question from a quiz'''
    questions = quiz.questions
    if n < 0 or n >= len(questions):
        return None
    d = []
    question = questions[n]
    if Response.query.filter_by(userID=user.id, qnID=question.id).first():
        return None
    qn_txt = question.question
    options = question.options
    if pre_shuffle:
        shuffle(options)
    opt_txt = {option.id : option.option for option in options}
    d.append(qn_txt)
    d.append(opt_txt)
    return d

def validate_quiz_stu(quizID):
    '''Validates a quizID link'''
    return Quiz.query.filter_by(id=quizID).first_or_404()

def validate_quiz_link(user, quizID):
    '''Validates a quizID link belonging to an educator'''
    return Quiz.query.filter_by(id=quizID,userID=user.id).first_or_404()

def validate_qn_link(qnID, userID):
    '''Validates question link belonging to an educator'''
    return Question.query.filter_by(id=qnID).filter(Question.quizzes.any(userID=userID)).first_or_404()

def add_topic(name):
    '''Adds a topic to the database'''
    topic = Topic(name=name)
    db.session.add(topic)
    db.session.commit()
    return topic


