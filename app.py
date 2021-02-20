from flask import Flask, request
from dotenv import load_dotenv
import os

import controllers
from controllers.helpers import create_session

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')


@app.route('/', methods=['GET'])
def index():
    return "Hello World"


@app.route('/login', methods=['POST'])
def login():
    return controllers.login(request, session)


@app.route('/logout', methods=['POST'])
def logout():
    return controllers.logout(request, session)



if __name__ == "__main__":
    session = create_session(os.getenv('DATABASE_URL'))
    app.run()
