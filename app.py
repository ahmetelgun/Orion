from flask import Flask, request
from dotenv import load_dotenv
import os

import controllers
from controllers.helpers import create_session

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')


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



if __name__ == "__main__":
    load_dotenv()
    session = create_session(os.getenv('DATABASE_URL'))
    app.run()
