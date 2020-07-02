import unittest
from app.tests.basetest import BaseTest
from app.models import *
from app.auth.email import generate_confirmation_token

from flask import url_for
from flask_login import current_user

class ForumTest(BaseTest):
    def test_create_thread(self):
        with self.app:
            self.login('testes@test.com', 'test')
            rv = self.app.post(url_for('forum.create_thread', groupID=1), data={'title': 'new test thread', 'content': 'new test post'}, follow_redirects=True)
            self.assertEqual(rv.status_code, 200)
            self.assertIn(b'new test thread', rv.data)
            self.assertIn(b'new test post', rv.data)
            self.assertIn(b'Your post is now live!', rv.data)

    def test_create_post(self):
        with self.app:
            self.login('testes@test.com', 'test')
            rv = self.app.post(url_for('forum.forum_post', groupID=1, threadID=1), data={'content': 'new test post'}, follow_redirects=True)
            self.assertEqual(rv.status_code, 200)
            self.assertIn(b'first thread', rv.data)
            self.assertIn(b'new test post', rv.data)
            self.assertIn(b'Your post is now live!', rv.data)

    def test_delete_post(self):
        with self.app:
            self.login('testes@test.com', 'test')
            rv = self.app.post(url_for('forum.delete_post', groupID=1, threadID=1, postID=1), data={}, follow_redirects=True)
            self.assertEqual(rv.status_code, 200)
            self.assertIn(b'Post deleted', rv.data)
            self.assertIn(b'first thread', rv.data)

    def test_delete_thread(self):
        with self.app:
            self.login('edutest@test.com', 'strongtest')
            rv = self.app.post(url_for('forum.delete_thread', groupID=1, threadID=1), data={}, follow_redirects=True)
            self.assertEqual(rv.status_code, 200)
            self.assertIn(b'Thread deleted', rv.data)
            self.assertIn(b'Create A New Thread', rv.data)


    def test_edit_post(self):
        with self.app:
            self.login('testes@test.com', 'test')
            rv = self.app.post(url_for('forum.edit_post', groupID=1, threadID=1, postID=1), data={'content':'edited post'}, follow_redirects=True)
            self.assertEqual(rv.status_code, 200)
            self.assertIn(b'first thread', rv.data)
            self.assertIn(b'edited post', rv.data)

if __name__ == '__main__':
    unittest.main()
