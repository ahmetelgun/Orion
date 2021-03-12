import unittest
import jwt
import os

from .fake_data import test_db
import app
from models import Author, Post


class TestDeletePost(unittest.TestCase):
    """
    /deletepost
    delete post

    {
        id: <int>
    }
    """
    def setUp(self):
        self.client = app.app.test_client()
        self.session = test_db()
        app.session = self.session

    def test_authentication(self):
        # no cookie
        res = self.client.post('/deletepost')
        self.assertEqual(res.status_code, 401)

        # invalid token
        self.client.set_cookie('localhost', 'token', '123')
        res = self.client.post('/deletepost')
        self.assertEqual(res.status_code, 401)

        # wrong token
        token = jwt.encode({'name': 'hello'}, os.getenv('SECRET_KEY'), algorithm='HS256')
        self.client.set_cookie('localhost', 'token', token)
        res = self.client.post('/deletepost')
        self.assertEqual(res.status_code, 401)

        # expired token
        token = self.session.query(Author).filter_by(
            username='thorin').first().token
        self.client.set_cookie('localhost', 'token', token)
        res = self.client.post('/deletepost')
        self.assertEqual(res.status_code, 401)

    def test_invalid_data(self):
        token = self.session.query(Author).filter_by(
            username='saruman').first().token
        self.client.set_cookie('localhost', 'token', token)

        # no data
        res = self.client.post('/deletepost')
        self.assertEqual(res.status_code, 400)

        # invalid data
        res = self.client.post('/deletepost', json={
            'idd': 1
        })
        self.assertEqual(res.status_code, 400)

    def test_authorization(self):
        token = self.session.query(Author).filter_by(
            username='saruman').first().token
        self.client.set_cookie('localhost', 'token', token)

        res = self.client.post('/deletepost', json={
            'id': 2
        })
        self.assertEqual(res.status_code, 401)
        self.assertEqual(res.json['message'], 'Unauthorized request')

    def test_non_exist_post(self):
        token = self.session.query(Author).filter_by(
            username='saruman').first().token
        self.client.set_cookie('localhost', 'token', token)

        res = self.client.post('/deletepost', json={
            'id': 99
        })
        self.assertEqual(res.status_code, 404)
        self.assertEqual(res.json['message'], 'Post not found')

    def test_success(self):
        token = self.session.query(Author).filter_by(
            username='saruman').first().token
        self.client.set_cookie('localhost', 'token', token)

        res = self.client.post('/deletepost', json={
            'id': 3
        })
        self.assertEqual(res.status_code, 200)
        self.assertIsNone(self.session.query(Post).filter_by(id=3).first())

