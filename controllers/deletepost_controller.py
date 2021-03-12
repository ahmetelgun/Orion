import os

from .helpers import response, create_token_cookie
from .authentication import is_login, refresh_jwt
from models import Post


def deletepost(request, session):
    if user := is_login(request.cookies.get('token'), os.getenv('SECRET_KEY'), session):
        token = refresh_jwt(request.cookies.get('token'),
                            os.getenv('SECRET_KEY'), 12, session)

    else:
        return response(
            data={
                'status': 'error',
                'message': 'Login required'},
            return_code=401,
            cookies=create_token_cookie()
        )

    try:
        data = request.json
        post_id = data['id']
        if not post_id:
            raise ValueError
        if not isinstance(post_id, int):
            raise TypeError
    except:
        return response(
            data={
                'status': 'error',
                'message': 'Invalid data'},
            return_code=400,
            cookies=create_token_cookie(token)
        )

    post = session.query(Post).filter_by(id=post_id).first()

    if not post:
        return response(
            data={
                'status': 'error',
                'message': 'Post not found'},
            return_code=404,
            cookies=create_token_cookie(token)
        )

    if post.author_id != user.id:
        return response(
            data={
                'status': 'error',
                'message': 'Unauthorized request'},
            return_code=401,
            cookies=create_token_cookie(token)
        )

    session.delete(post)
    session.commit()

    return response(
        data={
            'status': 'success',
            'message': 'Post successfuly deleted'},
        return_code=200,
        cookies=create_token_cookie(token)
    )