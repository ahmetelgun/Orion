import unittest
import os
from flask import json

from .fake_data import test_db
import app
from models import Author


class TestPostDetail(unittest.TestCase):
    def setUp(self):
        self.client = app.app.test_client()
        self.session = test_db()
        app.session = self.session

    def test_invalid_endpoint(self):
        res = self.client.get('/invalid-post-name')
        self.assertEqual(res.status_code, 404)

    def test_valid_endpoint(self):
        res = self.client.get('/what-is-cors')
        self.assertEqual(res.status_code, 200)
        data = res.json
        self.assertEqual(data['data']['name'], 'What is CORS?')
        self.assertEqual(data['data']['author']['name'], 'Gandalf the White')


        res = self.client.get('/what-is-linux')
        self.assertEqual(res.status_code, 200)
        data = res.json
        self.assertEqual(data['data']['name'], 'What is Linux?')
        self.assertEqual(data['data']['author']['name'], 'Saruman')