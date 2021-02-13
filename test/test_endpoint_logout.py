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

    def test_not_login(self):
        # no cookie
        res = self.client.post('/logout', json={})
        self.assertEqual(res.status_code, 406)

        # no login
        self.client.set_cookie('localhost', 'token', 'asdasd')
        res = self.client.post('/logout', json={})
        self.assertEqual(res.status_code, 406)

    def test_success_logout(self):
        user2 = self.session.query(Author).filter_by(username='saruman').first()
        self.client.set_cookie('localhost', 'token', user2.token)
        res = self.client.post('/logout', json={})
        self.assertEqual(res.status_code, 200)
