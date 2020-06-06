from app.models import User, Question, Option, Answer, Response

from catsim.simulation import *
# initialization package contains different initial proficiency estimation strategies
from catsim.initialization import *
# selection package contains different item selection strategies
from catsim.selection import *
# estimation package contains different proficiency estimation methods
from catsim.estimation import *
# stopping package contains different stopping criteria for the CAT
from catsim.stopping import *

from app.questions import get_items

# create a random proficiency initializer
initializer = RandomInitializer()

# create a maximum information item selector
selector = MaxInfoSelector()

# create a hill climbing proficiency estimator
estimator = HillClimbingEstimator()

# create a stopping criterion that will make tests stop after 20 items
stopper = MaxItemStopper(4)

items = get_items()

class Student(object):
    """Student Class used to apply CAT logic"""
    def __init__(self, id, theta=None, AI=None, responses=None):
        self.id = id
        self.theta = initializer.initialize() if theta is None else theta
        self.AI = [] if AI is None else AI
        self.responses = [] if responses is None else responses

    def get_next_question(self):
        if self.theta is None:
            self.theta = initializer.initialize()
        # get an estimated theta, given the answers to the dummy items
        new_theta = estimator.estimate(items=items, administered_items=self.AI, \
           response_vector=self.responses)
       
        # get the index of the next item to be administered to the current examinee, 
        # given the answers they have already given to the previous dummy items
        item_index = selector.select(items=items, administered_items=self.AI, \
           est_theta=self.theta)


        # get a boolean value pointing out whether the test should stop
        _stop = stopper.stop(administered_items=items[self.AI], theta=self.theta)

        if not _stop:
            return item_index

    def add_response(self, item, response):
        self.AI.append(item)
        self.responses.append(response)
