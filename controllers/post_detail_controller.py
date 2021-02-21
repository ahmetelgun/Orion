import os

from .authentication import is_login, refresh_jwt
from .helpers import response, create_token_cookie
from models import Post


def post_detail(request, session, endpoint):
    token = ''
    if is_login(request.cookies.get('token'), os.getenv('SECRET_KEY'), session):
        token = refresh_jwt(request.cookies.get('token'),
                            os.getenv('SECRET_KEY'), 12)

    post = session.query(Post).filter_by(endpoint=endpoint).first()
    if post:
        data = {
            'status': 'success',
            'data': {
                'name': post.name,
                'publish_date': post.publish_date,
                'endpoint': post.endpoint,
                'text': post.text,
                'author': {'name': post.author.name, 'username': post.author.username},
                'tags': [{'name': tag.name, 'endpoint': tag.endpoint} for tag in post.tags]
            }
        }
        return response(data, 200, create_token_cookie(token))

    return response({'status': 'not_found', 'message': 'Not found'}, 404, create_token_cookie(token))
