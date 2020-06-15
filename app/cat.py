from app.models import User, Question, Option, Answer, Response
from app import db

from catsim.simulation import *
# initialization package contains different initial proficiency estimation strategies
from catsim.initialization import *
# selection package contains different item selection strategies
from catsim.selection import *
# estimation package contains different proficiency estimation methods
from catsim.estimation import *
# stopping package contains different stopping criteria for the CAT
from catsim.stopping import *

from random import choice
import numpy

# create a random proficiency initializer
initializer = RandomInitializer()

# create a maximum information item selector
selector = MaxInfoSelector()

# create a hill climbing proficiency estimator
estimator = HillClimbingEstimator()

# create a stopping criterion that will make tests stop after 4 items
stopper = MaxItemStopper(4)

class Student(object):
    """Student Class used to apply CAT logic"""
    def __init__(self, id, topic=None, theta=None, AI=None, responses=None):
        self.id = id
        self.topic = 1 if topic is None else topic
        self.theta = initializer.initialize() if theta is None else theta
        self.AI = [] if AI is None else AI
        self.responses = [] if responses is None else responses
        self.items = self.get_items()

    def update(self):
        '''Updates theta and returns item_index'''
        # get an estimated theta, given the answers to the dummy items
        new_theta = estimator.estimate(items=self.items, administered_items=self.AI, \
           response_vector=self.responses, est_theta=self.theta)
       
        # get the index of the next item to be administered to the current examinee, 
        # given the answers they have already given to the previous dummy items
        item_index = selector.select(items=self.items, administered_items=self.AI, \
           est_theta=self.theta)
        
        self.theta = new_theta

        return item_index + 1

    def get_next_question(self):
        '''Get the next Question to be administered to the Student'''
        # Return a random question if no responses yet
        if not self.responses:
            qns = self.get_questions()
            qnIDs = [qn.id for qn in qns]
            return choice(qnIDs)

        item_index = self.update()

        if not self.stop():
            return item_index.item()

    def stop(self):
        '''Get boolean value whether the test should stop'''
        return stopper.stop(administered_items=self.items[self.AI], theta=self.theta)

    def get_items(self):
        '''Retrieve Question Item Bank from Database'''
        questions = self.get_questions()
        get_dis = lambda x:x.discrimination
        get_diff = lambda x:x.difficulty
        get_guess = lambda x:x.guessing
        get_upp = lambda x:x.upper
        get_params = [get_dis, get_diff, get_guess, get_upp]
        items = [[get(qn) for get in get_params] for qn in questions]
        return numpy.array(items)

    def get_questions(self):
        if self.topic == 1:
            return Question.query.all()
        else:
            return Question.query.filter_by(topic=self.topic).all()