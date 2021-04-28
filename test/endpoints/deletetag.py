import unittest

import app
from models import Author, Tag
from ..fake_data import test_db
from ..helpers import test_authentication


class TestDeleteTag(unittest.TestCase):
    """
    /deletetag
    delete new tag

    {
        name: <string>
    }
    """

    def setUp(self):
        self.client = app.app.test_client()
        self.session = test_db()
        app.session = self.session

    def test_generals(self):
        test_authentication(self, '/deletetag')

    def test_invalid_name(self):
        token = self.session.query(Author).filter_by(
            username='saruman').first().token
        self.client.set_cookie('localhost', 'token', token)

        # no data
        res = self.client.post('/deletetag')
        self.assertEqual(res.status_code, 400)

        # invlaid data
        res = self.client.post('/deletetag', json={
            'namee': 'Hello'
        })
        self.assertEqual(res.status_code, 400)

        # empty data
        res = self.client.post('/deletetag', json={
            'name': ''
        })
        self.assertEqual(res.status_code, 400)

        # non exist tag
        res = self.client.post('/deletetag', json={
            'name': 'Non Exist Tag'
        })
        self.assertEqual(res.status_code, 404)

    def test_success(self):
        token = self.session.query(Author).filter_by(
            username='saruman').first().token
        self.client.set_cookie('localhost', 'token', token)

        res = self.client.post('/deletetag', json={
            'name': 'Web development',
        })
        self.assertEqual(res.status_code, 200)
        self.assertIsNone(self.session.query(
            Tag).filter_by(name='Web development').first())
