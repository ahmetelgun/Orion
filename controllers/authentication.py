import jwt
import datetime
import os

from .helpers import get_time_after, response, create_token_cookie
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


def login_required(request, session):
    if user := is_login(request.cookies.get('token'), os.getenv('SECRET_KEY'), session):
        token = refresh_jwt(request.cookies.get('token'),
                            os.getenv('SECRET_KEY'), 12, session)
        return {'status': True, 'user': user, 'token': token}
    else:
        return {
            'status': False,
            'response': response(
                data={
                    'status': 'error',
                    'message': 'Login required'},
                return_code=401,
                cookies=create_token_cookie()
            )
        }
