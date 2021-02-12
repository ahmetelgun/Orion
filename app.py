from flask import Flask, request, jsonify
from dotenv import load_dotenv
from models import Author
import os
import controllers

app = Flask(__name__)
load_dotenv()

@app.route('/', methods=['GET'])
def index():
    return "Hello World"

@app.route('/login', methods=['POST'])
def hello_world():
    return controllers.login(request)
    

if __name__ == "__main__":
    app.run()