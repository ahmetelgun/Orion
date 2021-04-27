import unittest
import jwt
import os

import app
from models import Author, Post
from ..fake_data import test_db
from ..helpers import test_authentication

class TestCreatePost(unittest.TestCase):
    def setUp(self):
        self.client = app.app.test_client()
        self.session = test_db()
        app.session = self.session

    def test(self):
        test_authentication(self, '/createpost')

    def test_invalid_data_(self):
        token = self.session.query(Author).filter_by(
            username='saruman').first().token
        self.client.set_cookie('localhost', 'token', token)

        # no data
        res = self.client.post('/createpost')
        self.assertEqual(res.status_code, 400)

        # invlaid data
        res = self.client.post('/createpost', json={
            'namee': 'hello',
            'text': 'lorem ipsum dolor sit amet',
            'tags': ['Linux', 'JavaScript']
        })
        self.assertEqual(res.status_code, 400)

        res = self.client.post('/createpost', json={
            'name': 'hello',
            'textt': 'lorem ipsum dolor sit amet',
            'tags': ['Linux', 'JavaScript']
        })
        self.assertEqual(res.status_code, 400)

        # empty data
        res = self.client.post('/createpost', json={
            'name': '',
            'text': 'lorem ipsum dolor sit amet',
            'tags': ['Linux', 'JavaScript']
        })
        self.assertEqual(res.status_code, 400)

        res = self.client.post('/createpost', json={
            'name': 'hello',
            'text': '',
            'tags': ['Linux', 'JavaScript']
        })
        self.assertEqual(res.status_code, 400)

    def test_success(self):
        token = self.session.query(Author).filter_by(
            username='saruman').first().token
        self.client.set_cookie('localhost', 'token', token)

        # same name
        res = self.client.post('/createpost', json={
            'name': 'What is Linux?',
            'text': 'lorem ipsum dolor sit amet',
            'tags': ['Linux', 'JavaScript']
        })
        self.assertEqual(res.status_code, 200)

        last_post = self.session.query(Post).filter(Author.username == 'saruman').all()[-1]
        self.assertEqual(last_post.name, 'What is Linux?')
        self.assertNotEqual(last_post.endpoint, 'what-is-linux')

        # different name
        res = self.client.post('/createpost', json={
            'name': 'Lorem ipsum dolor sit amet',
            'text': 'lorem ipsum dolor sit amet',
            'tags': ['Linux', 'JavaScript']
        })
        self.assertEqual(res.status_code, 200)

        last_post = self.session.query(Post).filter(Author.username == 'saruman').all()[-1]
        self.assertEqual(last_post.name, 'Lorem ipsum dolor sit amet')
        self.assertEqual(last_post.endpoint, 'lorem-ipsum-dolor-sit-amet')
