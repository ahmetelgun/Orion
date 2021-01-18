from datetime import datetime as dtdt
import html
import jwt
from werkzeug.security import generate_password_hash
from config import database_url
import datetime as dt
from models import Author, create_session

def set_token_to_user(session, user, token):
    user.token = token
    session.add(user)
    session.commit()


def create_token(username, expiry_time, SECRET_KEY):
    token = jwt.encode(
        {"username": username, "exp": expiry_time.timestamp()}, SECRET_KEY, algorithm="HS256")
    return token.decode("utf-8")


def is_time_expire(expiry_time):
    now = dtdt.now()
    if now >= expiry_time:
        return True
    return False


def refresh_token(username, expiry_time, validity_days, refresh_time, SECRET_KEY):
    if (expiry_time - dtdt.now()) < dt.timedelta(hours=refresh_time):
        expiry_time = dtdt.now() + dt.timedelta(days=validity_days)
        token = create_token(username, expiry_time, SECRET_KEY)
        return token
    return False


def is_login(session, token, SECRET_KEY):
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        username = decoded['username']
        expiry_time = dtdt.fromtimestamp(decoded['exp'])
    except:
        return False

    if is_time_expire(expiry_time):
        return False

    user = session.query(Author).filter_by(username=username).first()
    if not user:
        return False

    if user.token != token:
        return False

    is_refresh = refresh_token(
        user.username, expiry_time, 1, 1, SECRET_KEY)
    if is_refresh:
        set_token_to_user(session, user, is_refresh)
    return user


def register_user(session, name=None, username=None, password=None):
    if name is None or username is None or password is None:
        print("Please enter your name, username and password")
        return 0
    if len(name) < 3 or len(name) > 32:
        print("name must be between 3 and 32 characters")
        return 1
    if len(username) < 3 or len(username) > 32:
        print("username must be between 3 and 32 characters")
        return 2
    if len(password) < 8 or len(password) > 32:
        print("password must be between 8 and 32 digits")
        return 3
    username = html.escape(username)
    name = html.escape(name)
    try:
        if session.query(Author).filter_by(username=username).first() is not None:
            print("This username already exist")
            return 4
    except:
        return 5
    user = Author(name=name, username=username)
    user.password = generate_password_hash(password)
    session.add(user)
    session.commit()
    print("user is created")
    return user


if __name__ == "__main__":
    name = input("name: ")
    username = input("username: ")
    password = input("password: ")
    session = create_session(database_url)
    register_user(session, name=name, username=username, password=password)
