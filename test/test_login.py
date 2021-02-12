import unittest
from app import app
from .fake_data import test_db

class TestLogin(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.session = test_db()
        
    def test_invalid_input(self):
        self.res = self.client.post('/login', json={})
        self.assertEqual(self.res.status_code, 400)

        self.res = self.client.post('/login', json={
            'username': 'ahmet'
        })
        self.assertEqual(self.res.status_code, 400)

        self.res = self.client.post('/login', json={
            'usernamee': 'ahmet'
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
            'usernamee': 'ahmet',
            'password': '12345678'
        })
        self.assertEqual(self.res.status_code, 400)

        self.res = self.client.post('/login', json={
            'username': 'ahmet',
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
            'username': 'ahmett',
            'password': '12345678'
        })
        self.assertEqual(self.res.status_code, 401)

    def test_wrong_password(self):
        self.res = self.client.post('/login', json={
            'username': 'ahmet',
            'password': ''
        })
        self.assertEqual(self.res.status_code, 401)

        self.res = self.client.post('/login', json={
            'username': 'ahmet',
            'password': '123456789'
        })
        self.assertEqual(self.res.status_code, 401)

    def test_success_login(self):
        self.res = self.client.post('/login', json={
            'username': 'ahmet',
            'password': '12345678'
        })
        self.assertEqual(self.res.status_code, 200)
