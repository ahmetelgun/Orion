import unittest
import jwt
from app import app
import datetime
from config import SECRET_KEY
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Author, Tag
from auth import create_token, set_token_to_user, is_login, register_user


def create_db():
  global engine, session, user, Session
  engine = create_engine("sqlite:///:memory:")
  Session = sessionmaker(bind=engine)
  session = Session()
  Base.metadata.create_all(engine)
  user = Author(name="a", username="a", password="12345678")
  tag1 = Tag(name="tag1")
  tag2 = Tag(name="tag2")
  session.add_all([user, tag1, tag2])
  session.commit()


class SetTokenToUserTestCase(unittest.TestCase):
  def test_set_token_to_user(self):
    token = "token"
    set_token_to_user(user, token, session)
    self.assertEqual(user.token, token)


class CreateTokenTestCase(unittest.TestCase):
  def test_create_token(self):
    time = datetime.datetime(5, 5, 1)
    token = jwt.encode(
        {"username": "a", "exp": time.timestamp()}, SECRET_KEY, algorithm="HS256").decode("utf-8")
    self.assertEqual(create_token("a", time), token)


class IsLoginTestCase(unittest.TestCase):
  def test_is_login(self):
    expiration_time = datetime.datetime.now() + datetime.timedelta(days=1)
    token = create_token(user.username, expiration_time)
    expired_token = create_token(
        user.username, datetime.datetime.now())
    false_token = create_token("b", expiration_time)

    set_token_to_user(user, token, session)
    request1 = app.test_request_context(
        '/login', method='POST', json={"username": "a", "password": "qwer1234"})
    request2 = app.test_request_context(
        '/login', method='POST', json={"token": token})
    request3 = app.test_request_context(
        '/login', method='POST', json={"username": "a", "password": "qwer1234", "token": token})
    request4 = app.test_request_context(
        '/login', method='POST', json={"username": "a", "password": "qwer12345", "token": token})
    request5 = app.test_request_context(
        '/login', method='POST', json={"username": "a", "password": "qwer1234", "token": expired_token})
    request6 = app.test_request_context(
        '/login', method='POST', json={"username": "a", "password": "qwer1234", "token": false_token})
    self.assertEqual(is_login(request1.request, session), False)
    self.assertEqual(is_login(request2.request, session), user)
    self.assertEqual(is_login(request3.request, session), user)
    self.assertEqual(is_login(request4.request, session), user)
    self.assertEqual(is_login(request5.request, session), False)
    self.assertEqual(is_login(request6.request, session), False)


class RegisterUserTestCase(unittest.TestCase):
  def test_register_user(self):
    user1 = register_user(
        session=session, name="a",
        username=user.username, password="12345678", )
    user2 = register_user(
        session=session, name="qwe",
        username="abc", password="123"
    )
    user3 = register_user(
        session=session, name="a",
        username="abd", password="123456789012345678901234567890123"
    )
    user4 = register_user(
        session=session, name="",
        username="abe", password="12345678"
    )
    user5 = register_user(
        session=session, name="qwe",
        username="", password="12345678"
    )
    user6 = register_user(
        session=session, name="qwe",
        username="abe", password="12345678"
    )
    self.assertFalse(user1)
    self.assertFalse(user2)
    self.assertFalse(user3)
    self.assertFalse(user4)
    self.assertFalse(user5)
    self.assertEqual(user6.username, "abe")


if __name__ == '__main__':
  create_db()
  unittest.main()
  engine.dispose()
  session.close()
