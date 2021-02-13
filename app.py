from flask import Flask, request
from dotenv import load_dotenv
import os

import controllers

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')


@app.route('/', methods=['GET'])
def index():
    return "Hello World"


@app.route('/login', methods=['POST'])
def login():
    return controllers.login(request)


@app.route('/logout', methods=['POST'])
def logout():
    return controllers.logout(request)


if __name__ == "__main__":
    app.run()
