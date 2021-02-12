import os
import jwt
from datetime import datetime

from .helpers import create_session
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
        if time > datetime.now().timestamp():
            return user
    return False
