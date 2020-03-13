from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from config import database_url

from werkzeug.security import generate_password_hash, check_password_hash

Base = declarative_base()


def create_database(database_url):
    try:
        engine = create_engine(database_url, echo=False)
        Base.metadata.create_all(engine)
    except Exception as e:
        print(e)


link = Table(
    'link',
    Base.metadata,
    Column('post_id', Integer, ForeignKey('posts.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True),
)


class Author(Base):
    __tablename__ = 'authors'
    id = Column(Integer, primary_key=True)
    name = Column(String(32), nullable=False)
    posts = relationship("Post", back_populates="author")
    username = Column(String(32), nullable=False, unique=True)
    password = Column(String(128), nullable=False)
    token = Column(String(128))


class Post(Base):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    published_date = Column(DateTime, nullable=False)
    text = Column(String, nullable=False)
    excerpt = Column(String, nullable=False)
    author_id = Column(Integer, ForeignKey('authors.id'))
    author = relationship("Author", back_populates="posts")
    tags = relationship(
        "Tag", secondary=link,
        back_populates="posts")


class Tag(Base):
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    posts = relationship(
        "Post", secondary=link, back_populates="tags")

    def __repr__(self):
        return repr({'id': self.id, 'name': self.name})


if __name__ == "__main__":
    create_database(database_url)
