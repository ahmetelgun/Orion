import os
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from werkzeug.security import generate_password_hash

import models

def create_test_database():
    TEST_DB = 'sqlite:///test.db'
    os.environ['DATABASE_URL'] = TEST_DB
    engine = models.create_database(TEST_DB, True)
    return engine

def create_test_data(session):
    user1_info = {
        'name': 'Ahmet Elgun',
        'username': 'ahmet',
        'password': generate_password_hash('12345678')
    }
    user1 = models.Author(**user1_info)
    session.add(user1)
    session.commit()

def test_db():
    engine = create_test_database()
    Session = sessionmaker(bind=engine)
    session = Session()
    create_test_data(session)
    return session