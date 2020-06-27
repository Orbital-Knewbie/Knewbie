import unittest
from app.tests.basetest import BaseTest
from flask import url_for

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


if __name__ == '__main__':
    unittest.main()
