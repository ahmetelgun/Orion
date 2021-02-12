import os
from flask import jsonify
from helpers import create_session
from models import Author
from werkzeug.security import check_password_hash

def login(request):
    session = create_session(os.getenv('DATABASE_URL'))
    data = request.json
    try:
        username = data['username']
        password = data['password']
    except:
        return jsonify({
            'status': 'error', 
            'message': 'Username or password invalid'
        }), 400

    user = session.query(Author).filter_by(username=username).first()
    
    if user and check_password_hash(user.password, password):
        return jsonify({
            'status': 'success',
            'message': 'Login success'
        }), 200

    return jsonify({
        'status': 'error',
        'message': 'Username or password wrong'
    }), 401