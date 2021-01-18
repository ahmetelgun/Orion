import datetime as dt
from datetime import datetime as dtdt
from flask import Flask
import json
import jwt
import unittest
import app
from auth import create_token, set_token_to_user, is_login, register_user, is_time_expire, refresh_token
from models import Author, Tag, CustomPage, Post
from test_helpers import SECRET_KEY, create_db, login_user

"""
    set_token_to_user
    create_token
    is_time_expire
    refresh_token
    is_login
    register_user
"""


class AuthPyTestCase(unittest.TestCase):
    def test_set_token_to_user(self):
        session, user1, _ = create_db()
        token = "token"
        set_token_to_user(session, user1, token)
        self.assertEqual(user1.token, token)

    def test_create_token(self):
        time = dtdt(5, 5, 1)
        token = jwt.encode(
            {"username": "a", "exp": time.timestamp()}, SECRET_KEY, algorithm="HS256").decode("utf-8")
        self.assertEqual(create_token("a", time, SECRET_KEY), token)

    def test_is_time_expire(self):
        t = dtdt.now() - dt.timedelta(seconds=1)
        self.assertTrue(is_time_expire(t))

        t = dtdt.now() + dt.timedelta(seconds=1)
        self.assertFalse(is_time_expire(t))

    def test_refresh_token(self):
        expiry_time = dtdt.now() + dt.timedelta(hours=3)
        is_refresh = refresh_token("gandalf", expiry_time, 1, 1, "secret")
        self.assertEqual(is_refresh, False)

        expiry_time = dtdt.now() + dt.timedelta(hours=3)
        is_refresh = refresh_token("gandalf", expiry_time, 1, 4, "secret")
        self.assertEqual(type(is_refresh).__name__, "str")

    def test_is_login(self):
        session, _, _ = create_db()
        self.assertFalse(is_login(session, "token", "secret"))

        expiry_time = dtdt.now()
        token = create_token("gandalf", expiry_time, "secret")
        self.assertFalse(is_login(session, token, "secret"))

        expiry_time = dtdt.now() + dt.timedelta(days=1)
        token = create_token("balrog", expiry_time, "secret")
        self.assertFalse(is_login(session, token, "secret"))

        expiry_time1 = dtdt.now() + dt.timedelta(days=1)
        expiry_time2 = dtdt.now() + dt.timedelta(days=2)
        token1 = create_token("gandalf", expiry_time1, "secret")
        token2 = create_token("gandalf", expiry_time2, "secret")
        gandalf = session.query(Author).filter_by(
            username="gandalf").first()
        set_token_to_user(session, gandalf, token1)
        self.assertFalse(is_login(session, token2, "secret"))

        expiry_time = dtdt.now() + dt.timedelta(minutes=1)
        token = create_token("gandalf", expiry_time, "secret")
        gandalf = session.query(Author).filter_by(
            username="gandalf").first()
        set_token_to_user(session, gandalf, token)
        user = is_login(session, token, "secret")
        self.assertEqual(user.username, gandalf.username)
        self.assertNotEqual(token, user.token)

        expiry_time = dtdt.now() + dt.timedelta(hours=4)
        token = create_token("gandalf", expiry_time, "secret")
        gandalf = session.query(Author).filter_by(
            username="gandalf").first()
        set_token_to_user(session, gandalf, token)
        user = is_login(session, token, "secret")
        self.assertEqual(user.username, gandalf.username)
        self.assertEqual(token, user.token)

    def test_register_user(self):
        session, _, _ = create_db()

        self.assertEqual(register_user(
            session, "Saruman", "gandalf", "gandalfscum"), 4)
        self.assertEqual(register_user(
            "session", "Saruman", "crazyboy", "gandalfscum"), 5)
        self.assertEqual(register_user(session, "Saruman",
                                       "crazyboy", "gandalfscum").username, "crazyboy")


"""
    /login
    /logout
"""


class AuthenticationEndpoints(unittest.TestCase):
    def test_login_endpoint(self):
        session, _, user2 = create_db()
        c = app.app.test_client()

        res = c.post(
            "/login", json={"username": "asd", "password": "12345678"})
        self.assertEqual(res.status_code, 401)

        res = c.post("/login", json={"username": "", "password": "12345678"})
        self.assertEqual(res.status_code, 401)

        res = c.post("/login", json={"username": "gandalf", "password": ""})
        self.assertEqual(res.status_code, 401)

        res = c.post("/login", json={"password": "12345678"})
        self.assertEqual(res.status_code, 400)

        res = c.post("/login", json={"username": "gandalf"})
        self.assertEqual(res.status_code, 400)

        res = c.post("/login")
        self.assertEqual(res.status_code, 400)

        c.set_cookie("localhost", "token", "asdljnsadlksad")
        res = c.post("/login")
        self.assertEqual(res.status_code, 400)
        c.cookie_jar.clear()

        c.set_cookie("localhost", "token", "asdljnsadlksad")
        res = c.post(
            "/login", json={"username": "horsemaster", "password": "fudenethor"})
        self.assertEqual(res.status_code, 200)
        c.cookie_jar.clear()

        c.set_cookie("localhost", "token", "asdljnsadlksad")
        res = c.post(
            "/login", json={"username": "horsemaster", "password": "123"})
        self.assertEqual(res.status_code, 401)
        c.cookie_jar.clear()

        login_user(user2, session)
        c.set_cookie("localhost", "token", user2.token)
        res = c.post("/login")
        self.assertEqual(res.status_code, 200)
        c.cookie_jar.clear()

        res = c.post(
            "/login", json={"username": "gandalf", "password": "iloveugaladriel"})
        self.assertEqual(res.status_code, 200)

    def test_logout_endpoint(self):
        session, user1, _ = create_db()
        c = app.app.test_client()

        login_user(user1, session)
        c.set_cookie("localhost", "token", user1.token)
        res = c.post("/logout")
        self.assertEqual(res.status_code, 200)

        c.set_cookie("localhost", "token", "test")
        res = c.post("/logout")
        self.assertEqual(res.status_code, 404)


"""
    /posts
    /yyyy/mm/dd/name
    /createpost
    /editpost
"""


class PostEndpointsTestCase(unittest.TestCase):
    def test_postlist_endpoint(self):
        create_db()
        app.posts_per_page = 2
        c = app.app.test_client()

        res = c.get("/posts")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json['current_page'], 1)
        self.assertEqual(res.json['total_number_of_page'], 3)
        self.assertEqual(res.json['posts'][0]['name'], 'post5')
        self.assertEqual(res.json['posts'][1]['name'], 'post4')

        res = c.get("/posts?page=2")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json['current_page'], 2)
        self.assertEqual(res.json['total_number_of_page'], 3)
        self.assertEqual(res.json['posts'][0]['name'], 'post3')
        self.assertEqual(res.json['posts'][1]['name'], 'post2')

        res = c.get("/posts?page=4")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json['current_page'], 1)
        self.assertEqual(res.json['total_number_of_page'], 3)
        self.assertEqual(res.json['posts'][0]['name'], 'post5')
        self.assertEqual(res.json['posts'][1]['name'], 'post4')

        res = c.get("/posts?tag=tag2")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json['current_page'], 1)
        self.assertEqual(res.json['total_number_of_page'], 2)
        self.assertEqual(res.json['posts'][0]['name'], 'post4')
        self.assertEqual(res.json['posts'][1]['name'], 'post2')

        res = c.get("/posts?tag=notexisttag")
        self.assertEqual(res.status_code, 404)

        res = c.get("/posts?tag=tag2&page=1")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json['current_page'], 1)
        self.assertEqual(res.json['total_number_of_page'], 2)
        self.assertEqual(res.json['posts'][0]['name'], 'post4')
        self.assertEqual(res.json['posts'][1]['name'], 'post2')

        res = c.get("/posts?tag=tag2&page=2")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json['current_page'], 2)
        self.assertEqual(res.json['total_number_of_page'], 2)
        self.assertEqual(res.json['posts'][0]['name'], 'post1')

        res = c.get("/posts?tag=tag2&page=3")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json['current_page'], 1)
        self.assertEqual(res.json['total_number_of_page'], 2)
        self.assertEqual(res.json['posts'][0]['name'], 'post4')
        self.assertEqual(res.json['posts'][1]['name'], 'post2')

        res = c.get("/posts?tag=notexisttag&page=1")
        self.assertEqual(res.status_code, 404)

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

    def test_create_post_endpoint(self):
        session, user1, _ = create_db()
        c = app.app.test_client()
        login_user(user1, session)

        c.set_cookie("localhost", "token", "asdljnsadlksad")
        res = c.post(
            "/createpost", json={"post_name": "post_name", "post_text": "post_text"})
        self.assertEqual(res.status_code, 401)
        c.cookie_jar.clear()

        c.set_cookie("localhost", "token", user1.token)
        res = c.post("/createpost", json={"post_name": "post_name"})
        self.assertEqual(res.status_code, 400)

        c.set_cookie("localhost", "token", user1.token)
        res = c.post("/createpost", json={"post_text": "post_text"})
        self.assertEqual(res.status_code, 400)

        c.set_cookie("localhost", "token", user1.token)
        res = c.post("/createpost")
        self.assertEqual(res.status_code, 400)

        c.set_cookie("localhost", "token", user1.token)
        res = c.post("/createpost")
        self.assertEqual(res.status_code, 400)

        c.set_cookie("localhost", "token", user1.token)
        res = c.post(
            "/createpost", json={"post_name": "post_name", "post_text": "post_text"})
        self.assertEqual(res.status_code, 200)

        c.set_cookie("localhost", "token", user1.token)
        res = c.post(
            "/createpost", json={"post_name": "post_name", "post_text": "post_text2"})
        self.assertEqual(res.status_code, 409)

        c.set_cookie("localhost", "token", user1.token)
        res = c.post(
            "/createpost", json={"post_name": "post_name2", "post_text": "post_text", "tags": ["tag1"]})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(session.query(Post).all()[-1].tags[0].name, 'tag1')

    def test_editpost_endpoint(self):
        session, user1, user2 = create_db()
        c = app.app.test_client()
        login_user(user1, session)
        login_user(user2, session)

        res = c.post(
            "/editpost", json={"post_name": "updated name", "post_text": "updated text", "post_id": 1})
        self.assertEqual(res.status_code, 401)

        c.set_cookie("localhost", "token", "asdljnsadlksad")
        res = c.post(
            "/editpost", json={"post_name": "updated name", "post_text": "updated text", "post_id": 1})
        self.assertEqual(res.status_code, 401)

        c.set_cookie("localhost", "token", user1.token)
        res = c.post(
            "/editpost", json={"post_name": "updated name", "post_text": "updated text"})
        self.assertEqual(res.status_code, 400)

        c.set_cookie("localhost", "token", user1.token)
        res = c.post(
            "/editpost", json={"post_name": "updated name", "post_text": "updated text", "post_id": 4})
        self.assertEqual(res.status_code, 401)

        c.set_cookie("localhost", "token", user2.token)
        res = c.post(
            "/editpost", json={"post_name": "post4", "post_text": "updated text", "post_id": 5})
        self.assertEqual(res.status_code, 409)

        c.set_cookie("localhost", "token", user2.token)
        res = c.post(
            "/editpost", json={"post_name": "updated name", "post_text": "updated text", "post_id": 4})
        self.assertEqual(res.status_code, 200)


"""
    /taglist
    /createtag
"""


class TagEnpointsTestCase(unittest.TestCase):
    def test_tag_list_endpoint(self):
        create_db()
        c = app.app.test_client()
        res = c.get("/taglist")
        self.assertEqual(
            res.json, ["tag1", "tag2"])

    def test_create_tag_endpoint(self):
        session, user1, _ = create_db()
        c = app.app.test_client()
        login_user(user1, session)

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


"""
    /createcustompage
    /custompage
"""


class CustomPageEndpointsTestCase(unittest.TestCase):
    def test_createcustompage_endpoint(self):
        session, user1, _ = create_db()
        c = app.app.test_client()

        login_user(user1, session)

        res = c.post("/createcustompage",
                     json={"name": "test", "text": "text", "endpoint": "/testendoint"})
        self.assertEqual(res.status_code, 401)

        c.set_cookie("localhost", "token", "qwewqe")
        res = c.post("/createcustompage",
                     json={"name": "test", "text": "text", "endpoint": "/testendpoint"})
        self.assertEqual(res.status_code, 401)

        c.set_cookie("localhost", "token", user1.token)
        res = c.post("/createcustompage",
                     json={"text": "text", "endpoint": "/testendpoint"})
        self.assertEqual(res.status_code, 400)

        c.set_cookie("localhost", "token", user1.token)
        res = c.post("/createcustompage",
                     json={"name": "test", "text": "text", "endpoint": "/about"})
        self.assertEqual(res.status_code, 409)

        c.set_cookie("localhost", "token", user1.token)
        res = c.post("/createcustompage",
                     json={"name": "test", "text": "text", "endpoint": "/testendpoint"})
        self.assertEqual(res.status_code, 200)

    def test_custompage_endpoint(self):
        create_db()
        c = app.app.test_client()

        res = c.get("/about")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json['name'], "About")
        self.assertEqual(res.json['text'], "its my about")

        res = c.get("/contact")
        self.assertEqual(res.status_code, 404)


if __name__ == '__main__':
    unittest.main()
