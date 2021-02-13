import os
from sqlalchemy.orm import sessionmaker
from werkzeug.security import generate_password_hash

from controllers.token import create_user_token
from controllers.helpers import get_time_after
import models


def create_test_database():
    TEST_DB = 'sqlite:///test.db'
    os.environ['DATABASE_URL'] = TEST_DB
    engine = models.create_database(TEST_DB, True)
    return engine


def create_test_data(session):
    user1_info = {
        'name': 'Gandalf the White',
        'username': 'mithrandir',
        'password': generate_password_hash('12345678')
    }
    user1 = models.Author(**user1_info)

    expire = get_time_after(1, 0, 0)
    token = create_user_token('saruman', expire, os.getenv('SECRET_KEY'))
    user2_info = {
        'name': 'Saruman',
        'username': 'saruman',
        'password': generate_password_hash('qweqweqwe'),
        'token': token
    }
    user2 = models.Author(**user2_info)

    expire = get_time_after(0, 1, 0)
    token = create_user_token('theoden', expire, os.getenv('SECRET_KEY'))
    user3_info = {
        'name': 'Theoden',
        'username': 'theoden',
        'password': generate_password_hash('iamking'),
        'token': token
    }
    user3 = models.Author(**user3_info)

    session.add_all([user1, user2, user3])
    session.commit()


def test_db():
    engine = create_test_database()
    Session = sessionmaker(bind=engine)
    session = Session()
    create_test_data(session)
    return session
