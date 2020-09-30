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
    global user
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = app.create_session(engine)
    user = register_user(session, name="ahmet", username="a", password="12345678")
    tag1 = Tag(name="tag1")
    tag2 = Tag(name="tag2")
    post1 = Post(name="post1", published_date=datetime.datetime(2020, 5, 7, 15, 42, 0,0), text="post1 text", excerpt="post1 excerpt")
    post2 = Post(name="post2", published_date=datetime.datetime(2020, 6, 1, 12, 16, 0,0), text="post2 text", excerpt="post2 excerpt")
    post3 = Post(name="post3", published_date=datetime.datetime(2020, 7, 25, 5, 23, 0,0), text="post3 text", excerpt="post3 excerpt")
    post1.tags.append(tag1)
    post1.tags.append(tag2)
    post2.tags.append(tag2)
    post1.author = user
    post2.author = user
    post3.author = user
    session.add_all([tag1, tag2, post1, post2, post3])
    session.commit()

class AuthTestCase(unittest.TestCase):
    def test_login_endpoint(self):
        create_db()
        success = eval('{"login": True}')
        fail = eval('{"login": False, "message": "invalid username or password"}')
        
        c = app.app.test_client()
        res = c.post("/login", json={"username": "a", "password": "12345678"})
        self.assertEqual(res.json, success)
        c = app.app.test_client()
        c.set_cookie("localhost", "token", "asdljnsadlksad")
        res = c.post("/login", json={"username": "a", "password": "12345678"})
        self.assertEqual(res.json, success)
        c = app.app.test_client()
        c.set_cookie("localhost", "token", user.token)
        res = c.post("/login")
        self.assertEqual(res.json, success)

        c = app.app.test_client()
        res = c.post("/login", json={"username": "asd", "password": "12345678"})
        self.assertEqual(res.json, fail)
        c = app.app.test_client()
        res = c.post("/login", json={"username": "", "password": "12345678"})
        self.assertEqual(res.json, fail)
        c = app.app.test_client()
        res = c.post("/login", json={"password": "12345678"})
        self.assertEqual(res.json, fail)
        c = app.app.test_client()
        c.set_cookie("localhost", "token", "asdljnsadlksad")
        res = c.post("/login")
        self.assertEqual(res.json, fail)
        c = app.app.test_client()
        res = c.post("/login")
        self.assertEqual(res.json, fail)
    
    def test_logout_endpoint(self):
        create_db()
        c = app.app.test_client()
        c.post("/login", json={"username": "a", "password": "12345678"})
        c = app.app.test_client()
        c.set_cookie("localhost", "token", user.token)
        res = c.post("/logout")
        self.assertEqual(res.json["logout"], True)
        c = app.app.test_client()
        c.post("/login", json={"username": "a", "password": "12345678"})
        c = app.app.test_client()
        c.set_cookie("localhost", "token", "test")
        res = c.post("/logout")
        self.assertEqual(res.json["logout"], False)

class PostsEndpointTestCase(unittest.TestCase):
    def test_posts_endpoint(self):
        create_db()
        app.posts_per_page = 2
        c = app.app.test_client()
        res = c.get("/posts").json
        self.assertEqual(res['current_page'], 1)
        self.assertEqual(res['total_number_of_page'], 2)
        self.assertEqual(res['posts'][0], {'author': 'ahmet', 'author_id': 1, 'excerpt': 'post3 excerpt', 'id': 3, 'name': 'post3', 'published_date': '2020-07-25-05-23', 'tags': []})
        self.assertEqual(res['posts'][1], {'author': 'ahmet', 'author_id': 1, 'excerpt': 'post2 excerpt', 'id': 2, 'name': 'post2', 'published_date': '2020-06-01-12-16', 'tags': [{'id': 2, 'name': 'tag2'}]})
        c = app.app.test_client()
        res = c.get("/posts?page=2").json
        self.assertEqual(res['current_page'], 2)
        self.assertEqual(res['total_number_of_page'], 2)
        self.assertEqual(res['posts'][0], {'author': 'ahmet', 'author_id': 1, 'excerpt': 'post1 excerpt', 'id': 1, 'name': 'post1', 'published_date': '2020-05-07-15-42', 'tags': [{'id': 1, 'name': 'tag1'}, {'id': 2, 'name': 'tag2'}]})
        c = app.app.test_client()
        res = c.get("/posts?tag=tag2").json
        self.assertEqual(res['current_page'], 1)
        self.assertEqual(res['total_number_of_page'], 1)
        self.assertEqual(res['posts'][0], {'author': 'ahmet', 'author_id': 1, 'excerpt': 'post2 excerpt', 'id': 2, 'name': 'post2', 'published_date': '2020-06-01-12-16', 'tags': [{'id': 2, 'name': 'tag2'}]})
        self.assertEqual(res['posts'][1], {'author': 'ahmet', 'author_id': 1, 'excerpt': 'post1 excerpt', 'id': 1, 'name': 'post1', 'published_date': '2020-05-07-15-42', 'tags': [{'id': 1, 'name': 'tag1'}, {'id': 2, 'name': 'tag2'}]})
        c = app.app.test_client()
        res = c.get("/posts?tag=notexisttag").json
        self.assertEqual(res, {'message': 'tag not found'})
        c = app.app.test_client()
        res = c.get("/posts?page=notexistpage").json
        self.assertEqual(res['current_page'], 1)
        self.assertEqual(res['total_number_of_page'], 2)

class GetPostEndpointTestCase(unittest.TestCase):
    def test_get_post_endpoint(self):
        create_db()
        c = app.app.test_client()
        res = c.get("/2020/07/25/post3").json 
        self.assertEqual(res, {'author_id': 1, 'id': 3, 'name': 'post3', 'published_date': 'Sat, 25 Jul 2020 05:23:00 GMT', 'tags': [], 'text': 'post3 text'})
        c = app.app.test_client()
        res = c.get("/2020/06/01/post2").json 
        self.assertEqual(res, {'author_id': 1, 'id': 2, 'name': 'post2', 'published_date': 'Mon, 01 Jun 2020 12:16:00 GMT', 'tags': [{'id': 2, 'name': 'tag2'}], 'text': 'post2 text'})

class TagListEndpointTestCase(unittest.TestCase):
    def test_tag_list_endpoint(self):
        create_db()
        c = app.app.test_client()
        res = c.get("/taglist").json
        self.assertEqual(res, [{'id': 1, 'name': 'tag1'}, {'id': 2, 'name': 'tag2'}])

class CreatePostEndpointTestCase(unittest.TestCase):
    def test_create_post_endpoint(self):
        create_db()
        c = app.app.test_client()
        res = c.post("/login", json={"username": "a", "password": "12345678"})
        
        c = app.app.test_client()
        c.set_cookie("localhost", "token", "asdljnsadlksad")
        res = c.post("/createpost", json={"post_name": "post_name", "post_text": "post_text"}).json
        self.assertEqual(res, {'login': False, 'message': 'unauthorized request'})
        c = app.app.test_client()
        c.set_cookie("localhost", "token", user.token)
        res = c.post("/createpost", json={"post_name": "post_name", "post_text": "post_text", "tags": ["tag1", "tag2"]}).json
        self.assertEqual(res, {'message': 'post added'})
        self.assertEqual(session.query(Post).all()[-1].name, 'post_name')
        self.assertEqual(session.query(Post).all()[-1].text, 'post_text')
        self.assertEqual(session.query(Post).all()[-1].tags[0].name, 'tag1')
        self.assertEqual(session.query(Post).all()[-1].tags[1].name, 'tag2')
        c = app.app.test_client()
        c.set_cookie("localhost", "token", user.token)
        res = c.post("/createpost", json={ "post_text": "post_text", "tags": ["tag1", "tag2"]}).json
        self.assertEqual(res, {'message': 'post name or post body is invalid'})
        c = app.app.test_client()
        c.set_cookie("localhost", "token", user.token)
        res = c.post("/createpost", json={ "post_name": "post_name", "tags": ["tag1", "tag2"]}).json
        self.assertEqual(res, {'message': 'post name or post body is invalid'})

class CreateTagEndpointTestCase(unittest.TestCase):
    def test_create_tag_endpoint(self):
        create_db()
        c = app.app.test_client()
        res = c.post("/login", json={"username": "a", "password": "12345678"})

        c = app.app.test_client()
        c.set_cookie("localhost", "token", "asdljnsadlksad")
        res = c.post("/createtag", json={"tag_name": "tag3"}).json
        self.assertEqual(res, {'login': False, 'message': 'unauthorized request'})
        c = app.app.test_client()
        c.set_cookie("localhost", "token", user.token)
        res = c.post("/createtag").json
        self.assertEqual(res, {"message": "tag name is invalid"})
        c = app.app.test_client()
        c.set_cookie("localhost", "token", user.token)
        res = c.post("/createtag", json={"tag_name": "tag2"}).json
        self.assertEqual(res, {"message": "tag is exist"})
        c = app.app.test_client()
        c.set_cookie("localhost", "token", user.token)
        res = c.post("/createtag", json={"tag_name": "tag3"}).json
        self.assertEqual(res, {"message": "tag is added"})

class SetTokenToUserTestCase(unittest.TestCase):
    def test_set_token_to_user(self):
        create_db()
        token = "token"
        set_token_to_user(user, token, session)
        self.assertEqual(user.token, token)
        
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
    unittest.main()
