from .helpers import response, create_token_cookie
from .authentication import login_required
from models import Tag


def delete_tag(request, session):
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

    if tag := session.query(Tag).filter_by(name=tag_name).first():
        session.delete(tag)
        session.commit()
        return response(
            data={
                'status': 'success',
                'message': 'Tag successfuly deleted'},
            return_code=200,
            cookies=create_token_cookie(token)
        )

    return response(
        data={
            'status': 'error',
            'message': 'Tag not found'},
        return_code=404,
        cookies=create_token_cookie(token)
    )
