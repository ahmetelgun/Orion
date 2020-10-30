import unittest
import jwt
import datetime
from config import SECRET_KEY
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Author, Tag
from auth import create_token, set_token_to_user, is_login, register_user
from flask import Flask
import app
import json
from models import Post
import datetime


def create_db():
    global session
    global user1
    global user2
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = app.create_session(engine)
    app.session = session
    user1 = register_user(session, name="ahmet",
                          username="a", password="12345678")
    user2 = register_user(session, name="mehmet",
                          username="m", password="12345678")
    tag1 = Tag(name="tag1")
    tag2 = Tag(name="tag2")

    post1 = Post(name="post1", published_date=datetime.datetime(2019, 5, 7, 15, 42, 0, 0),
                 text="post1 text", excerpt="post1 excerpt", endpoint="/2019/5/7/post1", id=1)
    post2 = Post(name="post2", published_date=datetime.datetime(2020, 6, 1, 12, 16, 0, 0),
                 text="post2 text", excerpt="post2 excerpt", endpoint="/2020/6/1/post2", id=2)
    post3 = Post(name="post3", published_date=datetime.datetime(2020, 6, 25, 5, 23, 0, 0),
                 text="post3 text", excerpt="post3 excerpt", endpoint="/2020/6/25/post3", id=3)
    post4 = Post(name="post4", published_date=datetime.datetime(2020, 7, 25, 5, 23, 0, 0),
                 text="post4 text", excerpt="post4 excerpt", endpoint="/2020/7/25/post4", id=4)

    post1.tags.append(tag1)
    post1.tags.append(tag2)
    post2.tags.append(tag2)
    post4.tags.append(tag2)
    post1.author = user1
    post2.author = user1
    post3.author = user1
    post4.author = user2
    session.add_all([tag1, tag2, post1, post2, post3, post4])
    session.commit()


class AuthTestCase(unittest.TestCase):
    def test_login_endpoint(self):
        create_db()
        c = app.app.test_client()

        res = c.post(
            "/login", json={"username": "asd", "password": "12345678"})
        self.assertEqual(res.status_code, 401)

        res = c.post("/login", json={"username": "", "password": "12345678"})
        self.assertEqual(res.status_code, 401)

        res = c.post("/login", json={"password": "12345678"})
        self.assertEqual(res.status_code, 401)

        c.set_cookie("localhost", "token", "asdljnsadlksad")
        res = c.post("/login")
        self.assertEqual(res.status_code, 401)
        c.cookie_jar.clear()

        res = c.post("/login")
        self.assertEqual(res.status_code, 401)

        res = c.post("/login", json={"username": "a", "password": "12345678"})
        self.assertEqual(res.status_code, 200)

        c.set_cookie("localhost", "token", "asdljnsadlksad")
        res = c.post("/login", json={"username": "a", "password": "12345678"})
        self.assertEqual(res.status_code, 200)
        c.cookie_jar.clear()

        c.set_cookie("localhost", "token", user1.token)
        res = c.post("/login")
        self.assertEqual(res.status_code, 200)
        c.cookie_jar.clear()

    def test_logout_endpoint(self):
        create_db()
        c = app.app.test_client()

        c.post("/login", json={"username": "a", "password": "12345678"})
        c = app.app.test_client()
        c.set_cookie("localhost", "token", user1.token)
        res = c.post("/logout")
        self.assertEqual(res.status_code, 200)

        c = app.app.test_client()
        c.post("/login", json={"username": "a", "password": "12345678"})
        c = app.app.test_client()
        c.set_cookie("localhost", "token", "test")
        res = c.post("/logout")
        self.assertEqual(res.status_code, 400)


class PostsEndpointTestCase(unittest.TestCase):
    def test_posts_endpoint(self):
        create_db()
        app.posts_per_page = 2
        c = app.app.test_client()

        res = c.get("/posts")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json['current_page'], 1)
        self.assertEqual(res.json['total_number_of_page'], 2)
        self.assertEqual(res.json['posts'][0]['name'], 'post4')
        self.assertEqual(res.json['posts'][1]['name'], 'post3')

        res = c.get("/posts?page=2")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json['current_page'], 2)
        self.assertEqual(res.json['total_number_of_page'], 2)
        self.assertEqual(res.json['posts'][0]['name'], 'post2')
        self.assertEqual(res.json['posts'][1]['name'], 'post1')

        res = c.get("/posts?tag=tag2")
        self.assertEqual(res.json['current_page'], 1)
        self.assertEqual(res.json['total_number_of_page'], 2)
        self.assertEqual(res.json['posts'][0]['name'], 'post4')
        self.assertEqual(res.json['posts'][1]['name'], 'post2')

        res = c.get("/posts?tag=notexisttag")
        self.assertEqual(res.status_code, 404)


class GetPostEndpointTestCase(unittest.TestCase):
    def test_get_post_endpoint(self):
        create_db()
        c = app.app.test_client()

        res = c.get("/2020/6/25/post3")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json['name'], 'post3')

        res = c.get("/2020/06/01/post2")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json['name'], 'post2')

        res = c.get("/2020/06/01/post3")
        self.assertEqual(res.status_code, 404)


class TagListEndpointTestCase(unittest.TestCase):
    def test_tag_list_endpoint(self):
        create_db()
        c = app.app.test_client()
        res = c.get("/taglist")
        self.assertEqual(
            res.json, [{'id': 1, 'name': 'tag1'}, {'id': 2, 'name': 'tag2'}])


class CreatePostEndpointTestCase(unittest.TestCase):
    def test_create_post_endpoint(self):
        create_db()
        c = app.app.test_client()
        res = c.post("/login", json={"username": "a", "password": "12345678"})

        c.set_cookie("localhost", "token", "asdljnsadlksad")
        res = c.post(
            "/createpost", json={"post_name": "post_name", "post_text": "post_text"})
        self.assertEqual(res.status_code, 401)
        c.cookie_jar.clear()

        c.set_cookie("localhost", "token", user1.token)
        res = c.post("/createpost", json={"post_name": "post_name",
                                          "post_text": "post_text", "tags": ["tag1", "tag2"]})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(session.query(Post).all()[-1].name, 'post_name')
        self.assertEqual(session.query(Post).all()[-1].text, 'post_text')
        self.assertEqual(session.query(Post).all()[-1].tags[0].name, 'tag1')
        self.assertEqual(session.query(Post).all()[-1].tags[1].name, 'tag2')

        c.set_cookie("localhost", "token", user1.token)
        res = c.post(
            "/createpost", json={"post_text": "post_text", "tags": ["tag1", "tag2"]})
        self.assertEqual(res.status_code, 400)

        c.set_cookie("localhost", "token", user1.token)
        res = c.post(
            "/createpost", json={"post_name": "post_name", "tags": ["tag1", "tag2"]})
        self.assertEqual(res.status_code, 400)


class CreateTagEndpointTestCase(unittest.TestCase):
    def test_create_tag_endpoint(self):
        create_db()
        c = app.app.test_client()
        res = c.post("/login", json={"username": "a", "password": "12345678"})

        c.set_cookie("localhost", "token", "asdljnsadlksad")
        res = c.post("/createtag", json={"tag_name": "tag3"})
        self.assertEqual(res.status_code, 401)

        c.set_cookie("localhost", "token", user1.token)
        res = c.post("/createtag")
        self.assertEqual(res.status_code, 400)

        c.set_cookie("localhost", "token", user1.token)
        res = c.post("/createtag", json={"tag_name": "tag2"})
        self.assertEqual(res.status_code, 409)

        c.set_cookie("localhost", "token", user1.token)
        res = c.post("/createtag", json={"tag_name": "tag3"})
        self.assertEqual(res.status_code, 200)


class SetTokenToUserTestCase(unittest.TestCase):
    def test_set_token_to_user(self):
        create_db()
        token = "token"
        set_token_to_user(user1, token, session)
        self.assertEqual(user1.token, token)


class CreateTokenTestCase(unittest.TestCase):
    def test_create_token(self):
        create_db()
        time = datetime.datetime(5, 5, 1)
        token = jwt.encode(
            {"username": "a", "exp": time.timestamp()}, SECRET_KEY, algorithm="HS256").decode("utf-8")
        self.assertEqual(create_token("a", time), token)


class RegisterUserTestCase(unittest.TestCase):
    def test_register_user(self):
        create_db()

        test_user1 = register_user(
            session=session, name="Manwe",
            username=user1.username, password="12345678", )
        test_user2 = register_user(
            session=session, name="Irmo",
            username="Irmo", password="123"
        )
        test_user3 = register_user(
            session=session, name="Orome",
            username="orome", password="123456789012345678901234567890123"
        )
        test_user4 = register_user(
            session=session, name="",
            username="ulmo", password="12345678"
        )
        test_user5 = register_user(
            session=session, name="Aule",
            username="", password="12345678"
        )
        test_user6 = register_user(
            session=session, name="Melkor",
            username="melkor", password="12345678"
        )
        self.assertFalse(test_user1)
        self.assertFalse(test_user2)
        self.assertFalse(test_user3)
        self.assertFalse(test_user4)
        self.assertFalse(test_user5)
        self.assertEqual(test_user6.username, "melkor")


class EditPostEndpointTestCase(unittest.TestCase):
    def test_editpost_endpoint(self):
        create_db()
        c = app.app.test_client()

        res = c.post(
            "/editpost", json={"post_name": "updated name", "post_text": "updated text"})
        self.assertEqual(res.status_code, 401)

        expr = datetime.datetime.now() + datetime.timedelta(days=1)
        user1token = create_token("a", expr)
        user2token = create_token("m", expr)
        set_token_to_user(user1, user1token, session)
        set_token_to_user(user2, user2token, session)

        c.set_cookie("localhost", "token", "asdljnsadlksad")
        res = c.post(
            "/editpost", json={"post_name": "updated name", "post_text": "updated text"})
        self.assertEqual(res.status_code, 401)

        c.set_cookie("localhost", "token", user2token)
        res = c.post(
            "/editpost", json={"name": "updated name", "text": "updated text"})
        self.assertEqual(res.status_code, 400)

        c.set_cookie("localhost", "token", user1token)
        res = c.post(
            "/editpost", json={"name": "updated name", "text": "updated text", "id": 4})
        self.assertEqual(res.status_code, 401)

        c.set_cookie("localhost", "token", user2token)
        res = c.post(
            "/editpost", json={"name": "updated name", "text": "updated text", "id": 4})
        self.assertEqual(res.status_code, 200)


class CreateCustomPageEndpointTestCase(unittest.TestCase):
    def test_createcustompage_endpoint(self):
        create_db()
        c = app.app.test_client()

        expr = datetime.datetime.now() + datetime.timedelta(days=1)
        user1token = create_token("a", expr)
        set_token_to_user(user1, user1token, session)

        res = c.post("/createcustompage",
                     json={"name": "test", "text": "text", "endpoint": "/testendoint"})
        self.assertEqual(res.status_code, 401)

        c.set_cookie("localhost", "token", "qwewqe")
        res = c.post("/createcustompage",
                     json={"name": "test", "text": "text", "endpoint": "/testendoint"})
        self.assertEqual(res.status_code, 401)

        c.set_cookie("localhost", "token", user1token)
        res = c.post("/createcustompage",
                     json={"text": "text", "endpoint": "/testendoint"})
        self.assertEqual(res.status_code, 400)

        c.set_cookie("localhost", "token", user1token)
        res = c.post("/createcustompage",
                     json={"name": "test", "text": "text", "endpoint": "/testendoint"})
        self.assertEqual(res.status_code, 200)

        c.set_cookie("localhost", "token", user1token)
        res = c.post("/createcustompage",
                     json={"name": "test", "text": "text", "endpoint": "/testendoint"})
        self.assertEqual(res.status_code, 409)


if __name__ == '__main__':
    unittest.main()
