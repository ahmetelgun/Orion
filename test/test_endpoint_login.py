import unittest
import os

from .fake_data import test_db
from app import app
from models import Author
from controllers.helpers import create_session


class TestLogin(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.session = test_db()

    def test_invalid_input(self):
        res = self.client.post('/login', json={})
        self.assertEqual(res.status_code, 400)

        res = self.client.post('/login', json={
            'username': 'mithrandir'
        })
        self.assertEqual(res.status_code, 400)

        res = self.client.post('/login', json={
            'usernamee': 'mithrandir'
        })
        self.assertEqual(res.status_code, 400)

        res = self.client.post('/login', json={
            'password': '12345678'
        })
        self.assertEqual(res.status_code, 400)

        res = self.client.post('/login', json={
            'passwordd': '12345678'
        })
        self.assertEqual(res.status_code, 400)

        res = self.client.post('/login', json={
            'usernamee': 'mithrandir',
            'password': '12345678'
        })
        self.assertEqual(res.status_code, 400)

        res = self.client.post('/login', json={
            'username': 'mithrandir',
            'passwordd': '12345678'
        })
        self.assertEqual(res.status_code, 400)

    def test_wrong_username(self):
        res = self.client.post('/login', json={
            'username': '',
            'password': '12345678'
        })
        self.assertEqual(res.status_code, 401)

        res = self.client.post('/login', json={
            'username': 'mithrandirr',
            'password': '12345678'
        })
        self.assertEqual(res.status_code, 401)

    def test_wrong_password(self):
        res = self.client.post('/login', json={
            'username': 'mithrandir',
            'password': ''
        })
        self.assertEqual(res.status_code, 401)

        res = self.client.post('/login', json={
            'username': 'mithrandir',
            'password': '123456789'
        })
        self.assertEqual(res.status_code, 401)

        self.client.set_cookie('localhost', 'token', 'asdasd')
        res = self.client.post('/login', json={
            'username': 'mithrandir',
            'password': '123456789'
        })
        self.assertEqual(res.status_code, 401)

    def test_success_login(self):
        # login with username and password
        res = self.client.post('/login', json={
            'username': 'mithrandir',
            'password': '12345678'
        })
        self.assertEqual(res.status_code, 200)

        # login with token
        user2 = self.session.query(Author).filter_by(username='saruman').first()
        self.client.set_cookie('localhost', 'token', user2.token)
        res = self.client.post('/login')
        self.assertEqual(res.status_code, 200)
        token = next(
            (cookie.value for cookie in self.client.cookie_jar if cookie.name == 'token'),
            None
        )
        self.assertEqual(token, user2.token)

        # login with token but wrong username and password
        user2 = self.session.query(Author).filter_by(username='saruman').first()
        self.client.set_cookie('localhost', 'token', user2.token)
        res = self.client.post('/login', json={
            'username': 'mithrandir',
            'password': '12345678'
        })
        self.assertEqual(res.status_code, 200)

        # login with token but refresh token
        user3 = self.session.query(Author).filter_by(username='theoden').first()
        self.client.set_cookie('localhost', 'token', user3.token)
        res = self.client.post('/login')
        self.assertEqual(res.status_code, 200)
        token = next(
            (cookie.value for cookie in self.client.cookie_jar if cookie.name == 'token'),
            None
        )
        self.assertNotEqual(token, user3.token)