import unittest
import os

from .fake_data import test_db
import app
from controllers.authentication import is_login, set_token_to_user
from controllers.helpers import get_time_after
from controllers.token import create_user_token
from models import Author


class TestIsLogin(unittest.TestCase):
    def setUp(self):
        self.client = app.app.test_client()
        self.session = test_db()
        app.session = self.session

    def test_is_not_login(self):
        # no token in db for user
        expire = get_time_after(1, 0, 0)
        token = create_user_token(
            'mithrandir', expire, os.getenv('SECRET_KEY'))
        self.assertFalse(
            is_login(token, os.getenv('SECRET_KEY'), self.session))

        # user token and incomming token not match
        expire = get_time_after(2, 0, 0)
        token = create_user_token('saruman', expire, os.getenv('SECRET_KEY'))
        self.assertFalse(
            is_login(token, os.getenv('SECRET_KEY'), self.session))

        # invalid token
        self.assertFalse(
            is_login('asdasd', os.getenv('SECRET_KEY'), self.session))

        # expired token
        user = self.session.query(Author).filter_by(
            username='mithrandir').first()
        time = get_time_after(0, 0, 0)
        token = create_user_token('mithrandir', time, os.getenv('SECRET_KEY'))
        set_token_to_user('mithrandir', token, self.session)
        self.assertFalse(
            is_login(user.token, os.getenv('SECRET_KEY'), self.session))

    def test_is_login(self):
        user = self.session.query(Author).filter_by(username='saruman').first()
        self.assertEqual(user.username, is_login(
            user.token, os.getenv('SECRET_KEY'), self.session).username)
