import unittest
import os
from flask import json

from ..fake_data import test_db
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
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['data']['current_page'], 1)
        self.assertEqual(data['data']['total_page'], 2)

        self.assertEqual(data['data']['posts'][0]['name'], 'What is Flask?')
        self.assertEqual(data['data']['posts'][1]['name'], 'What is Linux?')

    def test_with_invalid_page(self):
        res = self.client.get('/posts?page')
        self.assertEqual(res.status_code, 200)
        data = res.json
        self.assertEqual(data['data']['current_page'], 1)

        res = self.client.get('/posts?page=')
        self.assertEqual(res.status_code, 200)
        data = res.json
        self.assertEqual(data['data']['current_page'], 1)

        res = self.client.get('/posts?page=a')
        self.assertEqual(res.status_code, 200)
        data = res.json
        self.assertEqual(data['data']['current_page'], 1)

    def test_with_valid_page(self):
        res = self.client.get('/posts?page=1')
        self.assertEqual(res.status_code, 200)
        data = res.json
        self.assertEqual(data['data']['current_page'], 1)

        res = self.client.get('/posts?page=2')
        self.assertEqual(res.status_code, 200)
        data = res.json
        self.assertEqual(data['data']['current_page'], 2)

        # not exist page
        res = self.client.get('/posts?page=50')
        self.assertEqual(res.status_code, 200)
        data = res.json
        self.assertEqual(data['data']['current_page'], 1)

    def test_with_invalid_tag(self):
        res = self.client.get('/posts?tag=asd')
        self.assertEqual(res.status_code, 404)

        res = self.client.get('/posts?tag=')
        self.assertEqual(res.status_code, 200)

    def test_with_valid_tag(self):
        res = self.client.get('/posts?tag=Web development')
        self.assertEqual(res.status_code, 200)
        data = res.json
        self.assertEqual(len(data['data']['posts']), 2)

        res = self.client.get('/posts?tag=Linux')
        self.assertEqual(res.status_code, 200)
        data = res.json
        self.assertEqual(len(data['data']['posts']), 2)

    def test_with_tag_and_page(self):
        # invalid tag invalid page
        res = self.client.get('/posts?tag=asd&page=a')
        self.assertEqual(res.status_code, 404)

        res = self.client.get('/posts?tag=&page=a')
        self.assertEqual(res.status_code, 200)
        data = res.json
        self.assertEqual(data['data']['current_page'], 1)

        # invalid tag valid page
        res = self.client.get('/posts?page=1&tag=asd')
        self.assertEqual(res.status_code, 404)

        res = self.client.get('/posts?page=2&tag=')
        self.assertEqual(res.status_code, 200)
        data = res.json
        self.assertEqual(data['data']['current_page'], 2)

        # valid tag invalid page
        res = self.client.get('/posts?page=a&tag=Linux')
        self.assertEqual(res.status_code, 200)
        data = res.json
        self.assertEqual(data['data']['current_page'], 1)

        res = self.client.get('/posts?page=&tag=Web development')
        self.assertEqual(res.status_code, 200)
        data = res.json
        self.assertEqual(data['data']['current_page'], 1)

        # valid tag valid page
        res = self.client.get('/posts?page=1&tag=Linux')
        self.assertEqual(res.status_code, 200)
        data = res.json
        self.assertEqual(data['data']['current_page'], 1)

        res = self.client.get('/posts?page=2&tag=Post')
        self.assertEqual(res.status_code, 200)
        data = res.json
        self.assertEqual(data['data']['current_page'], 2)