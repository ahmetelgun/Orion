from flask import Flask, request, jsonify, make_response
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker
from models import Post, Author, Tag
from config import database_url, posts_per_page
from werkzeug.security import check_password_hash
import datetime
from auth import set_token_to_user, create_token, is_login
import html

app = Flask(__name__)

def create_session(engine):
    global session
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


def make_response_with_token(body, token):
    resp = jsonify(body)
    resp.set_cookie("token", token, secure=True, httponly=True, samesite='Strict')
    return resp


@app.route('/login', methods=["POST"])
def login():
    global session
    user = is_login(request, session)
    if user:
        resp = make_response_with_token({"login": True}, user.token)
        return resp, 200
    try:
        content = request.json
        username = html.escape(content["username"])
        password = content["password"]
    except:  # if username or password not exist in request
        return jsonify({"login": False, "message": "invalid username or password"}), 401
    user = session.query(Author).filter_by(username=username).first()
    if user:
        if check_password_hash(user.password, password):
            expiration_time = datetime.datetime.now() + datetime.timedelta(days=1)
            token = create_token(user.username, expiration_time)
            set_token_to_user(user, token, session)
            resp = make_response_with_token({"login": True}, token)
            return resp, 200 
    return jsonify({"login": False, "message": "invalid username or password"}), 401


@app.route('/logout', methods=["POST"])
def logout():
    user = is_login(request, session)
    if user:
        user.token = ""
        session.add(user)
        session.commit()
        res = make_response_with_token({"logout": True}, "")
        return res, 200
    return jsonify({"logout": False}), 200


@app.route('/posts', methods=["GET"])
def posts():
    total_number_of_page = 1
    postslist = []
    tag = request.args.get('tag', default=None, type=str)
    if tag:
        tag = session.query(Tag).filter_by(name=tag).first()
        if tag:  # if tag from query string exists on database
            posts = session.query(Post)\
                .filter(Post.tags.contains(tag))\
                .group_by(Post).order_by(Post.published_date.desc()).all()
        else:
            return jsonify({"message": "tag not found"}), 404
    else:  # if not tag query in query string
        posts = session.query(Post).order_by(Post.published_date.desc()).all()
    if len(posts) > posts_per_page:
        if len(posts) % posts_per_page == 0:
            total_number_of_page = len(posts)/posts_per_page
        else:
            total_number_of_page = len(posts)//posts_per_page + 1
    page = request.args.get('page', default=1, type=int)
    if page <= total_number_of_page and page >= 1:
        current_page = page
    else:
        current_page = 1
    for post in posts[current_page*posts_per_page-posts_per_page: current_page*posts_per_page]:
        taglist = [{'id': tag.id, 'name': tag.name} for tag in post.tags]
        author_name = post.author.name
        post = post.__dict__
        post['author'] = author_name
        post['tags'] = taglist
        post.pop('_sa_instance_state', None)
        post['published_date'] = post['published_date']\
            .strftime('%Y-%m-%d-%H-%M')
        post.pop('text')
        postslist.append(post)
    return jsonify({"posts": postslist, 'current_page': current_page, 'total_number_of_page': total_number_of_page})


@app.route('/<int:year>/<int:month>/<int:day>/<string:name>')
def post(year, month, day, name):
    date = datetime.datetime(year, month, day, 0, 0)
    after_date = date + datetime.timedelta(days=1)
    posts = session.query(Post).filter(
        and_(Post.published_date < after_date, Post.published_date >= date)).all()

    for i in posts:
        lower = i.name.strip().replace(" ", "-").lower()
        if name == lower:
            res = i.__dict__
            tags = [tag.__dict__ for tag in i.tags]
            for tag in tags:
                tag.pop('_sa_instance_state', None)
            res['tags'] = tags
            res.pop('_sa_instance_state', None)
            res.pop('excerpt')
            return jsonify(res), 200
    return jsonify({"message": "post not found"}), 404


@app.route('/taglist')
def taglist():
    tags_all = session.query(Tag).all()
    tags = []
    for tag in tags_all:
        t = tag.__dict__
        t.pop('_sa_instance_state', None)
        tags.append(t)
    return jsonify(tags), 200


@app.route('/addpost', methods=["POST"])
def addpost():
    user = is_login(request, session)
    if not user:
        return jsonify({"login": False, "message": "unauthorized request"}), 401
    try:
        content = request.json
        post_name = html.escape(content["post_name"])
        post_text = content["post_text"]
    except:
        return jsonify({"message": "post name or post body is invalid"}), 400
    post_excerpt = post_text[:50]
    published_date = datetime.datetime.now()
    post = Post(name=post_name, published_date=published_date,
                text=post_text, excerpt=post_excerpt)
    try:
        tags = set([session.query(Tag)
                    .filter_by(name=i).first() for i in content['tags']])
        for tag in tags:
            if tag:
                post.tags.append(tag)
    except:
        pass
    post.author = user
    session.add(post)
    session.commit()
    return jsonify({"message": "post added"}), 200


@app.route('/createtag', methods=["POST"])
def addtag():
    user = is_login(request, session)
    if not user:
        return jsonify({"login": False, "message": "unauthorized request"}), 401
    try:
        content = request.json
        tag_name = content['tag_name']
    except:
        return jsonify({"message": "tag name is invalid"}), 400
    try:
        tag = Tag(name=tag_name)
        session.add(tag)
        session.commit()
    except:
        return jsonify({"message": "tag is exist"}), 409
    return jsonify({"message": "tag is added"}), 200


if __name__ == '__main__':
    engine = create_engine(database_url)
    create_session(engine)
    app.debug = True
    app.run()
