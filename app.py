from flask import Flask, request
from dotenv import load_dotenv
import os

import controllers
from controllers.helpers import create_session

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

@app.after_request
def apply_caching(response):
    response.headers["Access-Control-Allow-Origin"] = os.getenv('FRONTEND_URL')
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


@app.route('/<post_endpoint>')
def post_detail(post_endpoint):
    resp = controllers.post_detail(request, session, post_endpoint)
    session.close()
    return resp


if __name__ == "__main__":
    load_dotenv()
    session = create_session(os.getenv('DATABASE_URL'))
    app.run()
