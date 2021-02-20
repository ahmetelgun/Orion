import os

from .token import decode_token
from .helpers import response
from models import Author


def logout(request, session):
    payload = decode_token(request.cookies.get(
        'token'), os.getenv('SECRET_KEY'))
    if payload:
        username = payload['username']
        user = session.query(Author).filter_by(username=username).first()
        if user:
            user.token = ''
            session.add(user)
            session.commit()
            return response(
                data={
                    'status': 'success',
                    'message': 'Logout success'},
                return_code=200,
                cookies=''
            )
    return response(
        data={
            'status': 'success',
            'message': 'Logout success'},
        return_code=406,
        cookies=''
    )
