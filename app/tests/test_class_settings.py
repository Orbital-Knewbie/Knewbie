import unittest
from app.tests.basetest import BaseTest
from app.models import *

from flask import url_for
from flask_login import current_user

class ClassQuizTest(BaseTest):
    def test_add_classquiz(self):
        '''Adding a quiz to the class'''
        with self.app:
            self.login('edutest@test.com', 'strongtest')

            # Add first quiz
            self.app.post(url_for('quiz.createquiz'), data={'quiz-title':'new quiz'}, follow_redirects=True)
            quiz1 = Quiz.query.filter_by(name='new quiz').first()
            self.app.post(url_for('quiz.createqn', quizID=quiz1.id), data={'topic':1, 'qn':'testqn2', 'op1':'op1', 'op2':'op2','op3':'op3','op4':'op4','corrOp':1, 'complete' : True},follow_redirects=True)
            
            # Add second quiz
            self.app.post(url_for('quiz.createquiz'), data={'quiz-title':'new quiz 2'}, follow_redirects=True)
            quiz2 = Quiz.query.filter_by(name='new quiz 2').first()
            self.app.post(url_for('quiz.createqn', quizID=quiz2.id), data={'topic':1, 'qn':'testqn3', 'op1':'op1', 'op2':'op2','op3':'op3','op4':'op4','corrOp':1, 'complete' : True},follow_redirects=True)
            
            # Check quizzes in the class
            rv = self.app.post(url_for('group.add_class_quiz', groupID=1), data={'field':[quiz1.id,quiz2.id]}, follow_redirects=True)
            quiz1 = Quiz.query.filter_by(id=quiz1.id).filter(Quiz.groups.any(id=1)).first()
            quiz2 = Quiz.query.filter_by(id=quiz2.id).filter(Quiz.groups.any(id=1)).first()
            
            self.assertIsNotNone(quiz1)
            self.assertIsNotNone(quiz2)

            self.assertEqual(rv.status_code, 200)
            self.assertIn(b'Quizzes added', rv.data)

            # Add same quiz
            rv = self.app.post(url_for('group.add_class_quiz', groupID=1), data={'field':[quiz1.id]}, follow_redirects=True)
            self.assertEqual(rv.status_code, 200)
            self.assertIn(b'Quiz new quiz already added', rv.data)

            self.logout()

            # Student tries quiz
            self.login('testes@test.com', 'testtest')
            rv = self.app.get(url_for('quiz.edu_quiz', quizID=quiz1.id, qnNum=1), follow_redirects=True)
            self.assertEqual(rv.status_code, 200)
            self.assertIn(b'new quiz', rv.data)

    def test_reattempt_tailored(self):
        with self.app:
            self.login('testes@test.com', 'testtest')
            rv = self.app.post(url_for('quiz.reattempt'), follow_redirects=True)
            self.assertEqual(rv.status_code, 200)
            self.assertIn(b'TAILORED QUIZ', rv.data)

    def test_reattempt_edu(self):
        q = Quiz.query.first()
        g = Group.query.first()
        g.quizzes.append(q)
        db.session.commit()
        with self.app:
            self.login('testes@test.com', 'testtest')
            rv = self.app.post(url_for('quiz.reattempt_edu', quizID=1), follow_redirects=True)
            self.assertEqual(rv.status_code, 200)
            self.assertIn(b'testquiz', rv.data)

    def test_edit_class_name(self):
        with self.app:
            self.login('edutest@test.com', 'strongtest')
            rv = self.app.post(url_for('group.edit_class_name', groupID=1), data={'name-title':'new class name'}, follow_redirects=True)
            self.assertEqual(rv.status_code, 200)
            self.assertIn(b'Class Name Changed', rv.data)
            self.assertIn(b'new class name', rv.data)
            g = Group.query.filter_by(id=1).first()
            self.assertEqual(g.name, 'new class name')

    def test_update_class_code(self):
        with self.app:
            self.login('edutest@test.com', 'strongtest')
            g = Group.query.filter_by(id=1).first()
            self.assertEqual(g.classCode, '654321')
            rv = self.app.post(url_for('group.update_class_code', groupID=1), follow_redirects=True)
            self.assertEqual(rv.status_code, 200)
            self.assertNotEqual(g.classCode, '654321')
            self.assertIn(b'Your class code has been successfully updated!', rv.data)

    def test_get_class_settings(self):
        with self.app:
            self.login('edutest@test.com', 'strongtest')
            rv = self.app.get(url_for('group.class_settings', groupID=1), follow_redirects=True)
            self.assertEqual(rv.status_code, 200)
            
            self.logout()
            self.login('testes@test.com', 'testtest')
            rv = self.app.get(url_for('group.class_settings', groupID=1), follow_redirects=True)
            self.assertEqual(rv.status_code, 403)


if __name__ == '__main__':
    unittest.main()
