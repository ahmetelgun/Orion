import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask import make_response, jsonify


def create_session(DATABASE_URL):
    engine = create_engine(DATABASE_URL, echo=False)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


def create_token_cookie(cookie=None):
    if cookie:
        return [
            {
                'key': 'login',
                'value': 'true'
            },
            {
                'key': 'token',
                'value': cookie
            }
        ]
    return [
        {
            'key': 'login',
            'value': 'false'
        },
        {
            'key': 'token',
            'value': ''
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
