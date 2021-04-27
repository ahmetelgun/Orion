from .helpers import response, create_token_cookie
from .authentication import login_required
from models import Tag


def create_tag(request, session):
    is_login = login_required(request, session)
    if is_login['status']:
        user, token = is_login['user'], is_login['token']
    else:
        return is_login['response']

    try:
        data = request.json
        tag_name = data['name'].strip()
        if tag_name == '':
            raise ValueError
    except:
        return response(
            data={
                'status': 'error',
                'message': 'Invalid input'},
            return_code=400,
            cookies=create_token_cookie(token)
        )

    if session.query(Tag).filter_by(name=tag_name).first() is not None:
        return response(
            data={
                'status': 'error',
                'message': 'Duplicate tag name'},
            return_code=409,
            cookies=create_token_cookie(token)
        )

    session.add(Tag(
        name=tag_name
    ))

    session.commit()

    return response(
        data={
            'status': 'success',
            'message': 'Tag successfuly created'},
        return_code=200,
        cookies=create_token_cookie(token)
    )
