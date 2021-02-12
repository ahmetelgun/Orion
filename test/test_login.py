import unittest

from .fake_data import test_db
from app import app
from models import Author


class TestLogin(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.session = test_db()

    def test_invalid_input(self):
        self.res = self.client.post('/login', json={})
        self.assertEqual(self.res.status_code, 400)

        self.res = self.client.post('/login', json={
            'username': 'mithrandir'
        })
        self.assertEqual(self.res.status_code, 400)

        self.res = self.client.post('/login', json={
            'usernamee': 'mithrandir'
        })
        self.assertEqual(self.res.status_code, 400)

        self.res = self.client.post('/login', json={
            'password': '12345678'
        })
        self.assertEqual(self.res.status_code, 400)

        self.res = self.client.post('/login', json={
            'passwordd': '12345678'
        })
        self.assertEqual(self.res.status_code, 400)

        self.res = self.client.post('/login', json={
            'usernamee': 'mithrandir',
            'password': '12345678'
        })
        self.assertEqual(self.res.status_code, 400)

        self.res = self.client.post('/login', json={
            'username': 'mithrandir',
            'passwordd': '12345678'
        })
        self.assertEqual(self.res.status_code, 400)

    def test_wrong_username(self):
        self.res = self.client.post('/login', json={
            'username': '',
            'password': '12345678'
        })
        self.assertEqual(self.res.status_code, 401)

        self.res = self.client.post('/login', json={
            'username': 'mithrandirr',
            'password': '12345678'
        })
        self.assertEqual(self.res.status_code, 401)

    def test_wrong_password(self):
        self.res = self.client.post('/login', json={
            'username': 'mithrandir',
            'password': ''
        })
        self.assertEqual(self.res.status_code, 401)

        self.res = self.client.post('/login', json={
            'username': 'mithrandir',
            'password': '123456789'
        })
        self.assertEqual(self.res.status_code, 401)

        self.client.set_cookie('localhost', 'token', 'asdasd')
        self.res = self.client.post('/login', json={
            'username': 'mithrandir',
            'password': '123456789'
        })
        self.assertEqual(self.res.status_code, 401)

    def test_success_login(self):
        # login with username and password
        self.res = self.client.post('/login', json={
            'username': 'mithrandir',
            'password': '12345678'
        })
        self.assertEqual(self.res.status_code, 200)

        # login with token
        user2 = self.session.query(Author).filter_by(username='saruman').first()
        self.client.set_cookie('localhost', 'token', user2.token)
        self.res = self.client.post('/login')
        self.assertEqual(self.res.status_code, 200)

        # login with token but wrong username and password
        user2 = self.session.query(Author).filter_by(username='saruman').first()
        self.client.set_cookie('localhost', 'token', user2.token)
        self.res = self.client.post('/login', json={
            'username': 'mithrandir',
            'password': '12345678'
        })
        self.assertEqual(self.res.status_code, 200)