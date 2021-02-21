import os
from sqlalchemy.orm import sessionmaker
from werkzeug.security import generate_password_hash
import datetime

from controllers.token import create_user_token
from controllers.helpers import get_time_after
import models


def create_test_database():
    TEST_DB = 'sqlite:///:memory:'
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

    tag1 = models.Tag(
        name='Web development',
        endpoint='web_development'
    )

    tag2 = models.Tag(
        name='JavaScript',
        endpoint='javascript'
    )

    tag3 = models.Tag(
        name='Linux',
        endpoint='linux'
    )

    tag4 = models.Tag(
        name='Post',
        endpoint='post'
    )

    post1 = models.Post(
        name='What is CORS?',
        publish_date=datetime.datetime(2021, 1, 1),
        endpoint='what-is-cors',
        text='cross origin resource sharing',
        excerpt='cors',
        author=user1,
        tags=[tag1, tag4]
    )

    post2 = models.Post(
        name='What is Fetch?',
        publish_date=datetime.datetime(2021, 1, 2),
        endpoint='what-is-fetch',
        text='es6 feature',
        excerpt='fetch',
        author=user1,
        tags=[tag1, tag2, tag4]
    )

    post3 = models.Post(
        name='What is Linux?',
        publish_date=datetime.datetime(2021, 1, 3),
        endpoint='what-is-linux',
        text='a kernel',
        excerpt='linux',
        author=user2,
        tags=[tag3, tag4]
    )

    session.add_all([user1, user2, user3, post1, post2,
                     post3, tag1, tag2, tag3, tag4])
    session.commit()


def test_db():
    engine = create_test_database()
    Session = sessionmaker(bind=engine)
    session = Session()
    create_test_data(session)
    return session
