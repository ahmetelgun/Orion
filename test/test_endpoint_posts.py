import unittest
import os
from flask import json

from .fake_data import test_db
import app
from models import Author


class TestPosts(unittest.TestCase):
    def setUp(self):
        self.client = app.app.test_client()
        self.session = test_db()
        app.session = self.session

    def test_only_posts(self):
        res = self.client.get('/posts')
        self.assertEqual(res.status_code, 200)
        
        data = res.json
        self.assertEqual(data['current_page'], 1)
        self.assertEqual(data['total_page'], 2)
        self.assertEqual(data['page_capacity'], 2)

        self.assertEqual(data['posts'][0]['name'], 'What is Linux?')
        self.assertEqual(data['posts'][1]['name'], 'What is Fetch?')

    def test_with_invalid_page(self):
        res = self.client.get('/posts?page')
        self.assertEqual(res.status_code, 200)
        data = res.json
        self.assertEqual(data['current_page'], 1)

        res = self.client.get('/posts?page=')
        self.assertEqual(res.status_code, 200)
        data = res.json
        self.assertEqual(data['current_page'], 1)
        
        res = self.client.get('/posts?page=a')
        self.assertEqual(res.status_code, 200)
        data = res.json
        self.assertEqual(data['current_page'], 1)
        
    def test_with_valid_page(self):
        res = self.client.get('/posts?page=1')
        self.assertEqual(res.status_code, 200)
        data = res.json
        self.assertEqual(data['current_page'], 1)

        res = self.client.get('/posts?page=2')
        self.assertEqual(res.status_code, 200)
        data = res.json
        self.assertEqual(data['current_page'], 2)

        # not exist page        
        res = self.client.get('/posts?page=50')
        self.assertEqual(res.status_code, 200)
        data = res.json
        self.assertEqual(data['current_page'], 1)
        
