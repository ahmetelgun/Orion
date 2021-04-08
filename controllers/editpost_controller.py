import os

from .helpers import response, create_token_cookie
from .authentication import refresh_jwt, login_required
from models import Post, Tag


def editpost(request, session):
    is_login = login_required(request, session)
    if is_login['status']:
        user, token = is_login['user'], is_login['token']
    else:
        return is_login['response']

    try:
        data = request.json
        post_id = data['id']
        name = data['name']
        endpoint = data['endpoint']
        text = data['text']
        if endpoint == '' or text == '':
            raise ValueError

        try:
            tags = data['tags']
            if not isinstance(tags, list):
                raise ValueError
        except:
            tags = False

        try:
            excerpt = data['excerpt']
            if not isinstance(excerpt, str):
                raise ValueError
        except:
            excerpt = False
    except:
        return response(
            data={
                'status': 'error',
                'message': 'Required fields missing'},
            return_code=400,
            cookies=create_token_cookie(token)
        )

    post = session.query(Post).filter_by(id=post_id).first()
    if not post:
        return response(
            data={
                'status': 'error',
                'message': 'Post not found'},
            return_code=400,
            cookies=create_token_cookie(token)
        )

    if post.author.username != user.username:
        return response(
            data={
                'status': 'error',
                'message': 'Unauthorized request'},
            return_code=401,
            cookies=create_token_cookie(token)
        )

    endpoint_duplicate = session.query(
        Post).filter_by(endpoint=endpoint).first()
    if endpoint_duplicate and endpoint_duplicate.id != post.id:
        return response(
            data={
                'status': 'error',
                'message': 'Another post has this endpoint'},
            return_code=409,
            cookies=create_token_cookie(token)
        )

    if tags != False:
        tags = [tag_instance for tag in tags if (tag_instance := session.query(
            Tag).filter_by(endpoint=tag).first()) is not None]
        post.tags = tags

    if excerpt != False:
        post.excerpt = excerpt

    post.name = name
    post.endpoint = endpoint
    post.text = text

    session.add(post)
    session.commit()

    return response(
        data={
            'status': 'success',
            'message': 'Post successfuly updated'},
        return_code=200,
        cookies=create_token_cookie(token)
    )
