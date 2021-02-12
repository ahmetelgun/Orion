from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def create_session(DATABASE_URL):
    engine = create_engine(DATABASE_URL, echo=False)
    Session = sessionmaker(bind=engine)
    session = Session()

    return session