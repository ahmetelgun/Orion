import unittest

import app
from models import Author
from ..fake_data import test_db
from ..helpers import test_authentication


class TestCreateTag(unittest.TestCase):
    """
    /createtag
    create new tag

    {
        name: <string>
    }
    """

    def setUp(self):
        self.client = app.app.test_client()
        self.session = test_db()
        app.session = self.session

    def test_generals(self):
        test_authentication(self, '/createtag')

    def test_invalid_name(self):
        token = self.session.query(Author).filter_by(
            username='saruman').first().token
        self.client.set_cookie('localhost', 'token', token)

        # no data
        res = self.client.post('/createtag')
        self.assertEqual(res.status_code, 400)

        # invlaid data
        res = self.client.post('/createtag', json={
            'namee': 'Hello'
        })
        self.assertEqual(res.status_code, 400)

        # empty data
        res = self.client.post('/createtag', json={
            'name': ''
        })
        self.assertEqual(res.status_code, 400)

    def test_duplicate(self):
        token = self.session.query(Author).filter_by(
            username='saruman').first().token
        self.client.set_cookie('localhost', 'token', token)

        res = self.client.post('/createtag', json={
            'name': 'Linux',
        })
        self.assertEqual(res.status_code, 409)

    def test_success(self):
        token = self.session.query(Author).filter_by(
            username='saruman').first().token
        self.client.set_cookie('localhost', 'token', token)

        res = self.client.post('/createtag', json={
            'name': 'Git',
        })
        self.assertEqual(res.status_code, 200)
