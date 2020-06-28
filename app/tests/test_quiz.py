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

            rv = self.app.post(url_for('createqn', quizID=quiz.id), data={'topic':1, 'qn':'testqn', 'op1':'op1', 'op2':'op2','op3':'op3','op4':'op4', 'corrOp':1},follow_redirects=True)
            self.assertEqual(rv.status_code, 200)
            self.assertIn(b'Question added', rv.data)
            self.assertIn(b'Create A New Quiz', rv.data)
            self.assertIn(b'Select Topic', rv.data)
            self.assertIn(b'Input Question', rv.data)

            rv = self.app.post(url_for('createqn', quizID=quiz.id), data={'topic':1, 'qn':'testqn2', 'op1':'op1', 'op2':'op2','op3':'op3','op4':'op4','corrOp':1, 'complete' : True},follow_redirects=True)
            self.assertEqual(rv.status_code, 200)
            self.assertIn(b'Quiz was successfully created!', rv.data)


    def test_preview_quiz(self):
        '''Preview educator created quiz'''
        with self.app:
            self.login('edutest@test.com', 'strongtest')
            rv = self.app.get(url_for('preview_quiz',quizID=1), follow_redirects=True)
            self.assertEqual(rv.status_code, 200)
            self.assertIn(b'testquestion', rv.data)
            self.assertIn(b'testoption1', rv.data)
            self.assertIn(b'Answer: ', rv.data)

    def test_get_edit_qn(self):
        with self.app:
            self.login('edutest@test.com', 'strongtest')
            rv = self.app.get(url_for('editqn',qnID=1), follow_redirects=True)
            self.assertEqual(rv.status_code, 200)
            self.assertIn(b'testquestion', rv.data)
            self.assertIn(b'testoption1', rv.data)
            self.assertIn(b'Edit Question', rv.data)

    def test_edit_qn(self):
        with self.app:
            self.login('edutest@test.com', 'strongtest')
            rv = self.app.post(url_for('editqn', qnID=1), data={'topic':1, 'qn':'edited question', 'op1':'op1', 'op2':'op2','op3':'op3','op4':'op4','corrOp':1},follow_redirects=True)
            self.assertEqual(rv.status_code, 200)
            self.assertIn(b'Question Edited Successfully!', rv.data)

            rv = self.app.get(url_for('preview_quiz',quizID=1), follow_redirects=True)
            self.assertEqual(rv.status_code, 200)
            self.assertIn(b'edited question', rv.data)

    def test_tailored_qn(self):
        '''Submitting a question in tailored quiz'''
        with self.app:
            self.login('testes@test.com', 'test')
            rv = self.app.post(url_for('quiz'), data={'option':1}, follow_redirects=True)
            self.assertEqual(rv.status_code, 200)
            self.assertIn(b'TAILORED QUIZ', rv.data)

    def test_edu_qn(self):
        '''Starting educator quiz'''
        with self.app:
            self.login('testes@test.com', 'test')
            rv = self.app.get(url_for('edu_quiz', quizID=1, qnNum=1), follow_redirects=True)
            self.assertEqual(rv.status_code, 200)
            self.assertIn(b'testquiz', rv.data)

    def test_post_edu_qn(self):
        '''Completing educator quiz'''
        with self.app:
            self.login('testes@test.com', 'test')
            rv = self.app.post(url_for('edu_quiz', quizID=1, qnNum=1), data={'option':1}, follow_redirects=True)
            self.assertEqual(rv.status_code, 200)
            self.assertIn(b'testquiz', rv.data)
            self.assertIn(b'Score:', rv.data)

if __name__ == '__main__':
    unittest.main()
