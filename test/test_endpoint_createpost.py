import unittest
import jwt
import os

from .fake_data import test_db
import app
from models import Author, Post


class TestCreatePost(unittest.TestCase):
    def setUp(self):
        self.client = app.app.test_client()
        self.session = test_db()
        app.session = self.session

    def test_authentication(self):
        # no cookie
        res = self.client.post('/createpost')
        self.assertEqual(res.status_code, 401)

        # invalid token
        self.client.set_cookie('localhost', 'token', '123')
        res = self.client.post('/createpost')
        self.assertEqual(res.status_code, 401)

        # wrong token
        token = jwt.encode({'name': 'hello'}, os.getenv('SECRET_KEY'), algorithm='HS256')
        self.client.set_cookie('localhost', 'token', token)
        res = self.client.post('/createpost')
        self.assertEqual(res.status_code, 401)

        # expired token
        token = self.session.query(Author).filter_by(
            username='thorin').first().token
        self.client.set_cookie('localhost', 'token', token)
        res = self.client.post('/createpost')
        self.assertEqual(res.status_code, 401)

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
            'tags': ['linux', 'javascript']
        })
        self.assertEqual(res.status_code, 400)

        res = self.client.post('/createpost', json={
            'name': 'hello',
            'textt': 'lorem ipsum dolor sit amet',
            'tags': ['linux', 'javascript']
        })
        self.assertEqual(res.status_code, 400)

        # empty data
        res = self.client.post('/createpost', json={
            'name': '',
            'text': 'lorem ipsum dolor sit amet',
            'tags': ['linux', 'javascript']
        })
        self.assertEqual(res.status_code, 400)

        res = self.client.post('/createpost', json={
            'name': 'hello',
            'text': '',
            'tags': ['linux', 'javascript']
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
            'tags': ['linux', 'javascript']
        })
        self.assertEqual(res.status_code, 200)

        last_post = self.session.query(Post).filter(Author.username == 'saruman').all()[-1]
        self.assertEqual(last_post.name, 'What is Linux?')
        self.assertNotEqual(last_post.endpoint, 'what-is-linux')

        # different name
        res = self.client.post('/createpost', json={
            'name': 'Lorem ipsum dolor sit amet',
            'text': 'lorem ipsum dolor sit amet',
            'tags': ['linux', 'javascript']
        })
        self.assertEqual(res.status_code, 200)

        last_post = self.session.query(Post).filter(Author.username == 'saruman').all()[-1]
        self.assertEqual(last_post.name, 'Lorem ipsum dolor sit amet')
        self.assertEqual(last_post.endpoint, 'lorem-ipsum-dolor-sit-amet')
