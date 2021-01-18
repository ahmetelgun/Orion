from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import app
from auth import create_token, set_token_to_user, register_user
import datetime
from models import Base, Author, Tag, CustomPage, Post


SECRET_KEY = "secret"


def create_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    app.session = session
    app.SECRET_KEY = SECRET_KEY
    user1 = register_user(session, name="Gandalf",
                          username="gandalf", password="iloveugaladriel")
    user2 = register_user(session, name="Theoden",
                          username="horsemaster", password="fudenethor")
    tag1 = Tag(name="tag1")
    tag2 = Tag(name="tag2")

    post1 = Post(name="post1", published_date=datetime.datetime(2019, 5, 7, 15, 42, 0, 0),
                 text="post1 text", excerpt="post1 excerpt", endpoint="/2019/5/7/post1", id=1)
    post2 = Post(name="post2", published_date=datetime.datetime(2020, 6, 1, 12, 16, 0, 0),
                 text="post2 text", excerpt="post2 excerpt", endpoint="/2020/6/1/post2", id=2)
    post3 = Post(name="post3", published_date=datetime.datetime(2020, 6, 25, 5, 23, 0, 0),
                 text="post3 text", excerpt="post3 excerpt", endpoint="/2020/6/25/post3", id=3)
    post4 = Post(name="post4", published_date=datetime.datetime(2020, 7, 25, 5, 23, 0, 0),
                 text="post4 text", excerpt="post4 excerpt", endpoint="/2020/7/25/post4", id=4)
    post5 = Post(name="post5", published_date=datetime.datetime(2020, 7, 25, 7, 23, 0, 0),
                 text="post5 text", excerpt="post5 excerpt", endpoint="/2020/7/25/post5", id=5)

    custom = CustomPage(name="About", endpoint="/about", text="its my about")

    post1.tags.append(tag1)
    post1.tags.append(tag2)
    post2.tags.append(tag2)
    post4.tags.append(tag2)
    post1.author = user1
    post2.author = user1
    post3.author = user1
    post4.author = user2
    post5.author = user2
    session.add_all([tag1, tag2, post1, post2, post3, post4, custom])
    session.commit()
    return session, user1, user2


def login_user(user, session):
    expiration_time = datetime.datetime.now() + datetime.timedelta(days=1)
    token = create_token(user.username, expiration_time, SECRET_KEY)
    set_token_to_user(session, user, token)
