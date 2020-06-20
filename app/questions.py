from app import db
from app.models import Question, Option, Answer, Response, Proficiency, Topic, Group, User
from app.cat import Student

from flask_login import current_user

from random import choice, shuffle
from datetime import datetime
from catsim.cat import generate_item_bank

import glob, os, json

org_qns = {
    "Fill in the blank: 423 x 1000 = ____ x 10": {
        "answers": [
            "42300",
            "423",
            "4230",
            "423000"
        ],
        "difficulty": "Easy"
    },
    "Which of the following is closest to 1?": {
        "answers": [
            "4/5",
            "1/2",
            "2/3",
            "3/4"
        ],
        "difficulty": "Easy"
    },
    "Which of the following is the same as 2010 g?": {
        "answers": [
            "2 kg 10 g",
            "2 kg 1 g",
            "20 kg 1 g",
            "20 kg 10 g"
        ],
        "difficulty": "Easy"
    },
    "Find the value of (3y +1) / 4 , when y = 5": {
        "answers": [
            "4",
            "9",
            "8",
            "5"
        ],
        "difficulty": "Easy"
    },
    "The ratio of Rachel's age to Samy's age is 7 : 6.  Rachel is 4 years older than Samy. What is Samy's age this year?": {
        "answers": [
            "24",
            "10",
            "11",
            "28"
        ],
        "difficulty": "Easy"
    },
    "How many fifths are there in 2 3/5?": {
        "answers": [
            "13",
            "11",
            "3",
            "6"
        ],
        "difficulty": "Easy"
    },
    "The sum of 1/2 and 2/5 is the same as ___.": {
        "answers": [
            "0.900",
            "0.009",
            "0.090",
            "9.000"
        ],
        "difficulty": "Easy"
    },
    "What is the value of 36 + 24 / (9 - 3) + 2 x 5 ?": {
        "answers": [
            "50",
            "51",
            "60",
            "66"
        ],
        "difficulty": "Easy"
    },
    "Sally has 100 marbles and her brother has 300 marbles. Express Sally's marbles as a percentage of the total number of marbles they have altogether.": {
        "answers": [
            "25%",
            "33 1/3 %",
            "300%",
            "400%"
        ],
        "difficulty": "Easy"
    },
    "Mr Tan has an equal number of pens and pencils. He puts the pens in bundles of 8 and the pencils in bundles of 12. There are 15 bundles altogether. How many pens are there?": {
        "answers": [
            "72",
            "24",
            "48",
            "96"
        ],
        "difficulty": "Hard"
    },
    "3 ones, 4 tenths and 7 thousandths is ___": {
        "answers": [
            "3.407",
            "3.470",
            "3.047",
            "3.740"
        ],
        "difficulty": "Hard"
    },
    "Which of the following is equal to 0.25%?": {
        "answers": [
            "1/400",
            "1/25",
            "1/4",
            "25"
        ],
        "difficulty": "Hard"
    }
}

def clear_questions():
    for q in Question.query.all():
        db.session.delete(q)
        db.session.commit()
    for q in Option.query.all():
        db.session.delete(q)
        db.session.commit()
    for q in Answer.query.all():
        db.session.delete(q)
        db.session.commit()

def clear_responses():
    for r in Response.query.all():
        db.session.delete(r)
    db.session.commit()

clear_responses()

def add_qn(org_qns):
    '''Adds questions to the database, where questions are formatted to be in a dictionary
    {<question>:{'answer':<options>,'difficulty':<difficulty>}
    <questions> is str
    <options> is list of str
    <difficulty> is float (not added yet)
    '''
    clear_questions()
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
                ans = Answer()
                opt.answer = ans
                qn.answer = ans
                db.session.add(ans)
                db.session.flush()
                b=False
            
            db.session.commit()

add_qn(org_qns)

def insert_qns():
    '''Inserts questions formatted as a json file
    {<number>:{'answer':<extra text><answer>,'option_texts':<extra text><options>, 'question_text':<extra text><question><extra text>}}
    all are strings
    '''
    path = 'app/static/resources/questions'
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
                        ans = Answer(question=qn,option=o)
                        db.session.add(ans)

                db.session.commit()

def test_insert_qns():
    '''To test insert_qns() works'''
    insert_qns()
    questions = Question.query.all()
    for q in questions:
        options = Option.query.filter_by(qnID=q.id)
        answer = Answer.query.filter_by(question=question).first()
        print(q.question)
        for o in options:
            if o.id == answer.optID:
                ans_opt = o
            print(o.option)

        print("ANS" + o.option)

#test_insert_qns()


def get_question_options(student):
    '''Retrieve Question and Option from Database'''
    # Get the Question
    qnid = student.get_next_question()
    question = Question.query.filter_by(id=qnid).first()
    qn_txt = question.question

    # Get the Options
    options_query = Option.query.filter_by(qnID=qnid).all()
    shuffle(options_query)
    options = {x.id : x.option for x in options_query}

    return qn_txt, options

def submit_response(id, form):
    '''Submit Response to Database'''
    # Get the submitted Option
    optID = form.get('option')
    option = Option.query.filter_by(id=optID).first()
    qnID = option.qnID

    # Create a Response entry
    response = Response(userID=id,optID=option.id,qnID=option.qnID)

    # Save to DB
    db.session.add(response)
    db.session.commit()

    # Update topic proficiency
    qn = Question.query.filter_by(id=qnID).first()
    if qn.topicID > 1:
        update_proficiency(qn.id, qn.topicID)
    update_proficiency(qn.id)

def update_proficiency(qnID, topicID=1):
    qn = Question.query.filter_by(id=qnID).first()
    prof, topic_student = get_student_cat(current_user.id, topicID)
    topic_student.update()
    prof.theta = topic_student.theta
    if topicID == 1:
        current_user.curr_theta = topic_student.theta
    db.session.commit()

def add_proficiency(id):
    '''Add timestamped proficiency entity, done every completed quiz'''
    prof, student = get_student_cat(userID)
    new_prof = Proficiency(userID=userID, timestamp=datetime.now(), 
                           theta=student.theta, topicID=1)
    db.session.add(new_prof)
    db.session.commit()

def get_student_cat(userID, topicID=1):
    '''Returns proficiency, student (CAT object) given a userID and optional topicID
    Defaults to overall proficiency (topicID=1)'''

    prof = Proficiency.query.filter_by(userID=userID,topicID=topicID)
    if not prof.all():
        prof = create_student_prof(userID)
    else:
        prof = prof.order_by(Proficiency.timestamp.desc()).first()
    AI, responses = prof.get_AI_responses()

    student = Student(userID, topicID, prof.theta, AI, responses)
    return prof, student

def create_student_prof(userID):
    '''Creates a proficiency entity for a student'''
    if not Topic.query.all():
        add_topic("first")
    topics = db.session.query(Topic.id).all()
    student_cat = Student(userID)
    current_user.curr_theta = student_cat.theta
    for topic, in topics:            
        prof = Proficiency(userID=userID, timestamp=datetime.now(), 
                           theta=student_cat.theta, topicID=topic)
        db.session.add(prof)
    db.session.commit()
    return prof

def add_topic(name):
    '''Adds a topic to the database'''
    topic = Topic(name=name)
    db.session.add(topic)
    db.session.commit()

def add_question(qn_text, options, answer):
    '''Adds a question to the database
    Input
    qn_text : str
    options : seq of str
    answer : int (1 to 4)
    '''
    # Generate item parameters from CatSim
    item = generate_item_bank(1)[0]

    # Add question
    question = Question(question=qn_text, discrimination=item[0], \
        difficulty=item[1], guessing=item[2], upper=item[3])
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
            ans = Answer(question=qn,option=o)
            db.session.add(ans)
    db.session.commit()

def get_proficiencies(userID):
    '''Return list of (timestamp, proficiency) in chronological order'''
    profs = Proficiency.query.filter_by(userID=userID,topicID=1).order_by(Proficiency.timestamp.asc()).all()
    return [(prof.timestamp, prof.theta) for prof in profs]

def get_curr_prof(userID):
    '''Returns current proficiency of the user'''
    return get_proficiencies(userID)[-1][1]

def get_response_answer(id):
    '''Returns number of correct responses, 
    and dictionary with question : [options, response, answer]'''

    responses = Response.query.filter_by(userID=id).all()
    d={}
    correct = 0
    for r in responses:
        qnID = r.qnID
        qn_txt = Question.query.filter_by(id=qnID).first().question
        opt = Option.query.filter_by(qnID=qnID).all()
        opt_txt = []
        ans = Answer.query.filter_by(qnID=qnID).first().optID
        for i in range(len(opt)):
            opt_txt.append(opt[i].option)
            if opt[i].id == ans:
                ans_num = i
            if opt[i].id == r.optID:
                res_num = i
        if ans_num == res_num:
            correct += 1
        d[qn_txt]=[opt_txt,ans_num,res_num]

    print(d)
    return correct, d

def get_sorted_students(groupID):
    return User.query.filter_by(urole='student').\
        filter(User.groups.any(id=groupID)).order_by(User.curr_theta.desc()).all()