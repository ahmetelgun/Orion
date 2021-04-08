import os

from .helpers import response, create_token_cookie
from .authentication import refresh_jwt, login_required
from models import Post


def deletepost(request, session):
    is_login = login_required(request, session)
    if is_login['status']:
        user, token = is_login['user'], is_login['token']
    else:
        return is_login['response']

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
