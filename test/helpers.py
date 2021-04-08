import jwt
import os

from models import Author


def test_authentication(self, endpoint):
    # no cookie
    res = self.client.post(endpoint)
    self.assertEqual(res.status_code, 401)

    # invalid token
    self.client.set_cookie('localhost', 'token', '123')
    res = self.client.post(endpoint)
    self.assertEqual(res.status_code, 401)

    # wrong token
    token = jwt.encode({'name': 'hello'}, os.getenv(
        'SECRET_KEY'), algorithm='HS256')
    self.client.set_cookie('localhost', 'token', token)
    res = self.client.post(endpoint)
    self.assertEqual(res.status_code, 401)

    # expired token
    token = self.session.query(Author).filter_by(
        username='thorin').first().token
    self.client.set_cookie('localhost', 'token', token)
    res = self.client.post(endpoint)
    self.assertEqual(res.status_code, 401)
