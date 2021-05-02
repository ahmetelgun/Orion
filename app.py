from flask import Flask, request
from dotenv import load_dotenv
import os

import controllers
from controllers.helpers import create_session

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

load_dotenv()
session = create_session(os.getenv('DATABASE_URL'))

@app.after_request
def apply_caching(response):
    response.headers["Access-Control-Allow-Origin"] = os.getenv('FRONTEND_URL')
    response.headers["Access-Control-Allow-Headers"] = "content-type"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    return response


@app.route('/', methods=['GET'])
def index():
    return "Hello World"


@app.route('/login', methods=['POST'])
def login():
    resp = controllers.login(request, session)
    session.close()
    return resp


@app.route('/logout', methods=['POST'])
def logout():
    resp = controllers.logout(request, session)
    session.close()
    return resp


@app.route('/posts', methods=['GET'])
def posts():
    resp = controllers.posts(request, session)
    session.close()
    return resp


@app.route('/createpost', methods=['POST'])
def create_posts():
    resp = controllers.create_post(request, session)
    session.close()
    return resp


@app.route('/editpost', methods=['POST'])
def edit_post():
    resp = controllers.editpost(request, session)
    session.close()
    return resp


@app.route('/deletepost', methods=['POST'])
def delete_post():
    resp = controllers.deletepost(request, session)
    session.close()
    return resp


@app.route('/<post_endpoint>')
def post_detail(post_endpoint):
    resp = controllers.post_detail(request, session, post_endpoint)
    session.close()
    return resp


@app.route('/createtag', methods=['POST'])
def create_tag():
    resp = controllers.create_tag(request, session)
    session.close()
    return resp


@app.route('/deletetag', methods=['POST'])
def delete_tag():
    resp = controllers.delete_tag(request, session)
    session.close()
    return resp


if __name__ == "__main__":
    app.run()
