import os
import jwt
import datetime

from .helpers import create_session, get_time_after
from .token import create_user_token
from models import Author


def is_login(token, secret):
    try:
        data = jwt.decode(token, secret, algorithms='HS256')
        username = data['username']
        time = data['time']
    except:
        return False
    session = create_session(os.getenv('DATABASE_URL'))
    user = session.query(Author).filter_by(username=username).first()
    if user and user.token == token:
        if time > datetime.datetime.now().timestamp():
            return user
    return False


def set_token_to_user(username, token):
    session = create_session(os.getenv('DATABASE_URL'))
    user = session.query(Author).filter_by(username=username).first()
    if user:
        user.token = token
        session.add(user)
        session.commit()
        return True
    return False


def refresh_jwt(token, secret, refresh_hour):
    payload = jwt.decode(token, secret, algorithms='HS256')
    username = payload['username']
    time = payload['time']
    remaining_time = time - datetime.datetime.now().timestamp()
    refresh_time = datetime.timedelta(hours=refresh_hour).total_seconds()
    if remaining_time < refresh_time:
        new_token = create_user_token(
            username, get_time_after(2, 0, 0), secret)
        set_token_to_user(username, new_token)
        return new_token
    return token
