import os
import datetime

from .helpers import response, create_token_cookie, generate_endpoint_from_name, create_valid_name
from .authentication import refresh_jwt, login_required
from models import Post, Tag


def create_post(request, session):
    is_login = login_required(request, session)
    if is_login['status']:
        user, token = is_login['user'], is_login['token']
    else:
        return is_login['response']

    try:
        data = request.json
        name = create_valid_name(data['name'])
        text = data['text']
        endpoint = generate_endpoint_from_name(name)

        if endpoint == '' or text == '':
            raise ValueError

        try:
            tags = data['tags']
        except:
            tags = []

        try:
            excerpt = data['excerpt']
        except:
            excerpt = " ".join(text.split()[:20])
    except:
        return response(
            data={
                'status': 'error',
                'message': 'Invalid input'},
            return_code=400,
            cookies=create_token_cookie(token)
        )

    endpoint = generate_endpoint_from_name(name)
    while session.query(Post).filter_by(endpoint=endpoint).first() is not None:
        endpoint = generate_endpoint_from_name(name, True)

    tags = [tag_instance for tag in tags if (tag_instance := session.query(
        Tag).filter_by(endpoint=tag).first()) is not None]

    session.add(Post(
        name=name,
        publish_date=datetime.datetime.now(),
        endpoint=endpoint,
        text=text,
        excerpt=excerpt,
        author=user,
        tags=tags
    ))

    session.commit()

    return response(
        data={
            'status': 'success',
            'message': 'Post successfuly created'},
        return_code=200,
        cookies=create_token_cookie(token)
    )
