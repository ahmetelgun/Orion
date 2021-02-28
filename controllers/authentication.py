import jwt
import datetime

from .helpers import get_time_after
from .token import create_user_token, decode_token
from models import Author


def is_login(token, secret, session):
    try:
        payload = decode_token(token, secret)
        username = payload['username']
        time = payload['time']
    except:
        return False
    user = session.query(Author).filter_by(username=username).first()
    if user and user.token == token:
        if time > datetime.datetime.now().timestamp():
            return user
    return False


def set_token_to_user(username, token, session):
    user = session.query(Author).filter_by(username=username).first()
    if user:
        user.token = token
        session.add(user)
        session.commit()
        return True
    return False


def refresh_jwt(token, secret, refresh_hour, session):
    payload = jwt.decode(token, secret, algorithms='HS256')
    username = payload['username']
    time = payload['time']
    remaining_time = time - datetime.datetime.now().timestamp()
    refresh_time = datetime.timedelta(hours=refresh_hour).total_seconds()
    if remaining_time < refresh_time:
        new_token = create_user_token(
            username, get_time_after(2, 0, 0), secret)
        set_token_to_user(username, new_token, session)
        return new_token
    return token
