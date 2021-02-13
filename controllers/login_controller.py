import os
from werkzeug.security import check_password_hash

from models import Author
from .authentication import is_login, set_token_to_user, refresh_jwt
from .helpers import create_session, response, create_token_cookie, get_time_after
from .token import create_user_token


def login(request):
    if is_login(request.cookies.get('token'), os.getenv('SECRET_KEY')):
        token = refresh_jwt(request.cookies.get('token'), os.getenv('SECRET_KEY'), 12)
        return response(
            data={
                'status': 'success',
                'message': 'Login success'},
            return_code=200,
            cookies=create_token_cookie(token)
        )
    session = create_session(os.getenv('DATABASE_URL'))
    data = request.json
    try:
        username = data['username']
        password = data['password']
    except:
        return response(
            data={
                'status': 'error',
                'message': 'Username or password invalid'},
            return_code=400,
            cookies=create_token_cookie()
        )

    user = session.query(Author).filter_by(username=username).first()

    if user and check_password_hash(user.password, password):
        expire = get_time_after(5, 0, 0)
        token = create_user_token(
            user.username, expire, os.getenv('SECRET_KEY'))
        set_token_to_user(user.username, token)
        return response(
            data={
                'status': 'success',
                'message': 'Login success'},
            return_code=200,
            cookies=create_token_cookie(token)
        )

    return response(
        data={
            'status': 'error',
            'message': 'Username or password wrong'},
        return_code=401,
        cookies=create_token_cookie()
    )
