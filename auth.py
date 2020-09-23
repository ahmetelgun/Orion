import jwt
import datetime
from models import Author
from config import SECRET_KEY
from werkzeug.security import generate_password_hash
import html


def set_token_to_user(user, token, session):
    user.token = token
    session.add(user)
    session.commit()


def create_token(username, expiration_time):
    token = jwt.encode(
        {"username": username, "exp": expiration_time.timestamp()}, SECRET_KEY, algorithm="HS256")
    return token.decode("utf-8")


def is_login(request, session):
    try:
        token = request.headers.get("Authorization").split(" ")[1]
        decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        username = decoded['username']
        expiration_time = datetime.datetime.fromtimestamp(decoded['exp'])
    except:
        return False
    now = datetime.datetime.now()
    if now > expiration_time:
        return False
    user = session.query(Author).filter_by(username=username).first()
    if not user:
        return False
    if user.token != token:
        return False
    if (expiration_time - now) < datetime.timedelta(hours=12):
        expiration_time = datetime.datetime.now() + datetime.timedelta(days=1)
        token = create_token(user.username, expiration_time)
        set_token_to_user(user, token, session)
        return user
    return user


def register_user(session, name=None, username=None, password=None):
    if name is None or username is None or password is None:
        print("Please enter your name, user name and password")
        return False
    if len(name) == 0 or len(username) == 0:
        print("please enter both name and username")
        return False
    if len(password) < 8 or len(password) > 32:
        print("Your password must be between 8 and 32 digits")
        return False
    username = html.escape(username)
    name = html.escape(name)
    try:
        if session.query(Author).filter_by(username=username).first() is not None:
            print("This username already exist")
            return False
    except:
        return False
    user = Author(name=name, username=username)
    user.password = generate_password_hash(password)
    session.add(user)
    session.commit()
    print("user is created")
    return user
