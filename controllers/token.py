import jwt


def create_token(payload, secret):
    return jwt.encode(payload, secret, algorithm='HS256')


def decode_token(token, secret):
    try:
        return jwt.decode(token, secret, algorithms='HS256')
    except:
        return False


def create_user_token(username, time, secret):
    payload = {
        'username': username,
        'time': time
    }
    return create_token(payload, secret)
