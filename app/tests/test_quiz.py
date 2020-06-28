import unittest
from app.tests.basetest import BaseTest
from app.models import *

from flask import url_for
from flask_login import current_user

class QuizTest(BaseTest):
    def test_quiz(self):
        with self.app:
            self.login('testes@test.com', 'test')

            rv = self.app.get(url_for('quiz'))
            self.assertEqual(rv.status_code, 200)
            self.assertIn(b'TAILORED QUIZ', rv.data)

    def test_edu_quiz(self):
        with self.app:
            self.login('edutest@test.com', 'strongtest')

            rv = self.app.get(url_for('createquizsuccess', quizID=1))
            self.assertEqual(rv.status_code, 200)
            self.assertIn(b'Quiz was successfully created!', rv.data)

    def test_create_quiz(self):
        with self.app:
            self.login('edutest@test.com', 'strongtest')
            rv = self.app.post(url_for('createquiz'), data={'quiz-title':'new quiz'}, follow_redirects=True)
            self.assertEqual(rv.status_code, 200)
            self.assertIn(b'Create A New Quiz', rv.data)
            self.assertIn(b'Select Topic', rv.data)
            self.assertIn(b'Input Question', rv.data)

            quiz = Quiz.query.filter_by(name='new quiz').first()

            rv = self.app.post(url_for('createqn', quizID=quiz.id), data={'topic':1, 'qn':'testqn', 'op1':'op1', 'op2':'op2','op3':'op3','corrOp':1},follow_redirects=True)
            self.assertEqual(rv.status_code, 200)
            self.assertIn(b'Create A New Quiz', rv.data)
            self.assertIn(b'Select Topic', rv.data)
            self.assertIn(b'Input Question', rv.data)

            #rv = self.app.post(url_for('createqn', quizID=quiz.id), data={'topic':1, 'qn':'testqn2', 'op1':'op1', 'op2':'op2','op3':'op3','corrOp':1},follow_redirects=True)
            #self.assertEqual(rv.status_code, 200)
            #self.assertIn(b'Quiz was successfully created!', rv.data)

if __name__ == '__main__':
    unittest.main()
