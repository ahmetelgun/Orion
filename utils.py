import contextlib
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@contextlib.contextmanager
def db_session(database_url):
    session = None
    try:
        engine = create_engine(database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        yield session
    finally:
        if session:
            session.close()
