import unittest
import jwt
import os

import app
from models import Author, Post
from ..fake_data import test_db
from ..helpers import test_authentication


class TestEditPost(unittest.TestCase):
    """
    /editpost
    update name, endpoint, text and tags of the post with /editpost
    publish date and author not changeable

    {
        id: <int>,
        name: <string>,
        endpoint: <string>,
        text: <string>,
        excerpt: <string>,      (OPTIONAL)
        tags: <array>           (OPTIONAL)
    }
    """

    def setUp(self):
        self.client = app.app.test_client()
        self.session = test_db()
        app.session = self.session

    def test(self):
        test_authentication(self, '/editpost')

    def test_authorization(self):
        token = self.session.query(Author).filter_by(
            username='saruman').first().token
        self.client.set_cookie('localhost', 'token', token)

        # user2 trying update the  user1's post
        res = self.client.post('/editpost', json={
            'id': 1,
            'name': 'What is CORS?',
            'endpoint': 'what-is-cors',
            'text': 'lorem ipsum dolor sit amet'
        })
        self.assertEqual(res.status_code, 401)

        data = res.json
        self.assertEqual(data['status'], 'error')
        self.assertEqual(data['message'], 'Unauthorized request')

    def test_invalid_data(self):
        token = self.session.query(Author).filter_by(
            username='saruman').first().token
        self.client.set_cookie('localhost', 'token', token)

        # no data
        res = self.client.post('/editpost')
        self.assertEqual(res.status_code, 400)

        # no id
        res = self.client.post('/editpost', json={
            'name': 'What is CORS?',
            'endpoint': 'what-is-cors',
            'text': 'lorem ipsum dolor sit amet'
        })
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json['message'], 'Required fields missing')

        # no name
        res = self.client.post('/editpost', json={
            'id': 1,
            'endpoint': 'what-is-cors',
            'text': 'lorem ipsum dolor sit amet'
        })
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json['message'], 'Required fields missing')

        # no endpoint
        res = self.client.post('/editpost', json={
            'id': 1,
            'name': 'What is CORS?',
            'text': 'lorem ipsum dolor sit amet'
        })
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json['message'], 'Required fields missing')

        # no text
        res = self.client.post('/editpost', json={
            'id': 1,
            'name': 'What is CORS?',
            'endpoint': 'what-is-cors',
        })
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json['message'], 'Required fields missing')

    def test_non_exist_post(self):
        token = self.session.query(Author).filter_by(
            username='saruman').first().token
        self.client.set_cookie('localhost', 'token', token)

        res = self.client.post('/editpost', json={
            'id': 999,
            'name': 'What is CORS?',
            'endpoint': 'what-is-cors',
            'text': 'lorem ipsum dolor sit amet'
        })
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json['message'], 'Post not found')

        res = self.client.post('/editpost', json={
            'id': 'asd',
            'name': 'What is CORS?',
            'endpoint': 'what-is-cors',
            'text': 'lorem ipsum dolor sit amet'
        })
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json['message'], 'Post not found')

        res = self.client.post('/editpost', json={
            'id': '',
            'name': 'What is CORS?',
            'endpoint': 'what-is-cors',
            'text': 'lorem ipsum dolor sit amet'
        })
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json['message'], 'Post not found')

    def test_endpoint_duplicate(self):
        token = self.session.query(Author).filter_by(
            username='saruman').first().token
        self.client.set_cookie('localhost', 'token', token)

        res = self.client.post('/editpost', json={
            'id': 3,
            'name': 'What is CORS?',
            'endpoint': 'what-is-flask',
            'text': 'lorem ipsum dolor sit amet'
        })
        self.assertEqual(res.status_code, 409)

    def test_success(self):
        token = self.session.query(Author).filter_by(
            username='saruman').first().token
        self.client.set_cookie('localhost', 'token', token)

        res = self.client.post('/editpost', json={
            'id': 3,
            'name': 'What is Linux?(UPDATED)',
            'endpoint': 'what-is-linux-updated',
            'text': 'lorem ipsum dolor sit amet updated',
            'tags': ['hello'],
            'excerpt': 'Lorem ipsum'
        })
        self.assertEqual(res.status_code, 200)
        post = self.session.query(Post).filter_by(id=3).first()
        self.assertEqual(post.name, 'What is Linux?(UPDATED)')
        self.assertEqual(len(post.tags), 0)
