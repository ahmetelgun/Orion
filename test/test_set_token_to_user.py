import unittest

from .fake_data import test_db
from app import app
from models import Author
from controllers.authentication import set_token_to_user


class TestSetTokenToUser(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.session = test_db()

    def test_wrong_username(self):
        self.assertFalse(set_token_to_user('sarumann', 'token'))

    def test_success(self):
        self.assertTrue(set_token_to_user('saruman', 'token'))
        
        set_token_to_user('saruman', 'token2')
        user = self.session.query(Author).filter_by(username='saruman').first()
        self.assertEqual(user.token, 'token2')