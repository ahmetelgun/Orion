import os
import sys
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

from models import Author
from controllers.helpers import create_session



def createUser(name, username, password):
    load_dotenv()
    session = create_session(os.getenv('DATABASE_URL'))
    author = Author(name=name, username=username,
                    password=generate_password_hash(password))
    session.add(author)
    session.commit()


if __name__ == "__main__":
    name = sys.argv[1]
    username = sys.argv[2]
    password = sys.argv[3]
    print(name)
    print(username)
    print(password)
    createUser(name, username, password)
