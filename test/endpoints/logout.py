import unittest

from ..fake_data import test_db
import app
from models import Author


class TestLogout(unittest.TestCase):
    def setUp(self):
        self.client = app.app.test_client()
        self.session = test_db()
        app.session = self.session

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
