import os
from .helpers import create_session, response, create_token_cookie
from models import Author
from werkzeug.security import check_password_hash

def login(request):
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
        return response(
            data={
                'status': 'success',
                'message': 'Login success'},
            return_code=200,
            cookies=create_token_cookie()
        )

    return response(
        data={
            'status': 'error',
            'message': 'Username or password wrong'},
        return_code=401,
        cookies=create_token_cookie()
    )