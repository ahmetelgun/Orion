import unittest
import jwt
import os

import app
from models import Author, Post
from ..fake_data import test_db
from ..helpers import test_authentication


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

    def test(self):
        test_authentication(self, '/deletepost')

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

