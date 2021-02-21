import os
import math

from .authentication import is_login, refresh_jwt
from .helpers import create_session, response, create_token_cookie
from models import Post, Tag


def posts(request, session):
    token = ''
    if is_login(request.cookies.get('token'), os.getenv('SECRET_KEY'), session):
        token = refresh_jwt(request.cookies.get('token'),
                            os.getenv('SECRET_KEY'), 12)
    try:
        page = int(request.args.get('page'))
    except:
        page = 1
    tag = request.args.get('tag')

    total_page = math.ceil(session.query(Post).count() /
                           int(os.getenv('POSTS_PER_PAGE')))
    if not isinstance(page, int) or (page > total_page or page < 1):
        page = 1
    last_index = page * int(os.getenv('POSTS_PER_PAGE'))
    first_index = (page - 1) * int(os.getenv('POSTS_PER_PAGE'))

    if tag:
        post_tag = session.query(Tag).filter_by(name=tag).first()
        if post_tag:
            posts = session.query(Post)\
                .filter(Post.tags.contains(post_tag))\
                .group_by(Post).order_by(Post.publish_date.desc())[first_index:last_index]
        else:
            return response(
                data={
                    'status': 'not_found',
                    'message': 'Tag not found'
                },
                return_code=404,
                cookies=create_token_cookie(token)
            )
    else:
        posts = session.query(Post)\
            .order_by(Post.publish_date.desc())[first_index:last_index]

    data = {
        'status': 'success',
        'data': {
            'total_page': total_page,
            'current_page': page,
            'posts': []
        }
    }

    for post in posts:
        temp = {
            'name': post.name,
            'publish_date': post.publish_date,
            'endpoint': post.endpoint,
            'excerpt': post.excerpt,
            'author': post.author.name,
            'tags': [tag.name for tag in post.tags]
        }
        data['data']['posts'].append(temp)

    return response(data, 200, create_token_cookie(token))
