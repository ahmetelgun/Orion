import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask import make_response, jsonify
import string
import random
import html
import os


def create_session(DATABASE_URL):
    engine = create_engine(DATABASE_URL, echo=False)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


def create_token_cookie(cookie=None):
    return [
        {
            'key': 'login',
            'value': "true" if cookie else "false",
            'max_age': 60*60*24*2,
            'httponly': False,
            'secure': True,
            'path': '/',
            'domain': os.getenv('FRONTEND_DOMAIN'),
            'samesite': 'Strict',
        },
        {
            'key': 'token',
            'value': cookie if cookie else "",
            'max_age': 60*60*24*2,
            'httponly': True,
            'secure': True,
            'path': '/',
            'domain': os.getenv('FRONTEND_DOMAIN'),
            'samesite': 'Strict',
        }
    ]


def response(data, return_code, cookies=[]):
    resp = make_response(jsonify(data))
    for cookie in cookies:
        resp.set_cookie(**cookie)
    return resp, return_code


def get_time_after(days, hours, minutes):
    now = datetime.datetime.now()
    time_after = now + \
        datetime.timedelta(days=days, hours=hours, minutes=minutes)
    return time_after.timestamp()


def generate_endpoint_from_name(name, exist=False):
    name = name.translate(str.maketrans('', '', string.punctuation))
    name = name.lower()
    name = name + ' '
    if exist:
        name += str(random.randint(1000, 9999))
    return "-".join(name.split())


def create_valid_name(name):
    return html.escape(" ".join(name.split()))
