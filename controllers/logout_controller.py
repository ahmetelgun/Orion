import os

from .helpers import response, create_token_cookie
from .authentication import is_login


def logout(request, session):
    try:
        user = is_login(request.cookies.get('token'),
                        os.getenv('SECRET_KEY'), session)
        user.token = ""
        session.add(user)
        session.commit()

        return response(
            data={
                'status': 'success',
                'message': 'Logout success'},
            return_code=200,
            cookies=create_token_cookie()
        )

    except:
        return response(
            data={
                'status': 'error',
                'message': 'Logout fail'},
            return_code=406,
            cookies=create_token_cookie()
        )
