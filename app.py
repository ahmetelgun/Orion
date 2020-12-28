from flask import Flask, request, jsonify, make_response
from sqlalchemy import create_engine, and_
from models import Post, Author, Tag, CustomPage
from config import database_url, posts_per_page
from werkzeug.security import check_password_hash
import datetime
from auth import set_token_to_user, create_token, is_login
import html
import string
import random
from sqlalchemy import func
from models import create_session
app = Flask(__name__)

engine = create_engine(database_url)
session = create_session(engine)
app.debug = True


def make_response_with_token(body, token):
    resp = jsonify(body)
    if token == "":
        is_login = "false"
    else:
        is_login = "true"

    resp.set_cookie("isLogin", is_login, samesite='Strict')
    resp.set_cookie("token", token, secure=True,
                    httponly=True, samesite='Strict')
    return resp


@app.route('/login', methods=["POST"])
def login():
    user = is_login(request, session)
    if user:
        resp = make_response_with_token({"login": True}, user.token)
        return resp, 200
    try:
        content = request.json
        username = html.escape(content["username"])
        password = content["password"]
    except:
        return make_response_with_token({"login": False, "message": "invalid username or password"}, ""), 400
    user = session.query(Author).filter_by(username=username).first()
    if user:
        if check_password_hash(user.password, password):
            expiration_time = datetime.datetime.now() + datetime.timedelta(days=1)
            token = create_token(user.username, expiration_time)
            set_token_to_user(user, token, session)
            return make_response_with_token({"login": True}, token), 200
    return make_response_with_token({"login": False, "message": "invalid username or password"}, ""), 401


@app.route('/logout', methods=["POST"])
def logout():
    user = is_login(request, session)
    if user:
        user.token = ""
        session.add(user)
        session.commit()
        return make_response_with_token({"logout": True}, ""), 200
    return make_response_with_token({"message": "user not exist"}, ""), 404


@app.route('/posts', methods=["GET"])
def posts():
    user = is_login(request, session)
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
            if user:
                return make_response_with_token({"message": "tag not found"}, user.token), 404
            return make_response_with_token({"message": "tag not found"}, ""), 404
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
        taglist = [{'name': tag.name} for tag in post.tags]
        author_name = post.author.name
        post = post.__dict__
        post.pop('author_id')
        post['author'] = author_name
        post['tags'] = taglist
        post.pop('_sa_instance_state', None)
        post['published_date'] = post['published_date']\
            .strftime('%d.%m.%Y')
        post.pop('text')
        postslist.append(post)
    body = {"posts": postslist, 'current_page': current_page,
            'total_number_of_page': total_number_of_page}
    if user:
        return make_response_with_token(body, user.token), 200
    return make_response_with_token(body, ""), 200


@app.route('/<int:year>/<int:month>/<int:day>/<string:name>', methods=["GET"])
def post(year, month, day, name):
    user = is_login(request, session)
    endpoint = f"/{year}/{month}/{day}/{name}"
    post = session.query(Post).filter_by(endpoint=endpoint).first()
    if post:
        res = post.__dict__
        tags = [tag.__dict__ for tag in post.tags]
        for tag in tags:
            tag.pop('_sa_instance_state', None)
            tag.pop('id')
        res['tags'] = tags
        res['published_date'] = res['published_date']\
            .strftime('%d.%m.%Y')
        res.pop('_sa_instance_state', None)
        res.pop('excerpt')
        res.pop('author_id')
        if user:
            return make_response_with_token(res, user.token), 200
        return make_response_with_token(res, ""), 200
    if user:
        return make_response_with_token({"message": "post not found"}, user.token), 404
    return make_response_with_token({"message": "post not found"}, ""), 404


@app.route('/taglist', methods=["GET"])
def taglist():
    user = is_login(request, session)
    tags_all = session.query(Tag).all()
    tags = [tag.name for tag in tags_all]
    if user:
        return make_response_with_token(tags, user.token), 200
    return make_response_with_token(tags, ""), 200


@app.route('/createpost', methods=["POST"])
def addpost():
    user = is_login(request, session)
    if not user:
        return make_response_with_token({"message": "unauthorized request"}, ""), 401

    try:
        content = request.json
        post_name = html.escape(content["post_name"])
        post_text = content["post_text"]
    except:
        return make_response_with_token({"message": "post name or post body invalid"}, user.token), 400

    published_date = datetime.datetime.now()
    endpoint = f"/{published_date.year}/{published_date.month}/{published_date.day}/{'-'.join(post_name.split()).lower()}"
    if session.query(Post).filter_by(endpoint=endpoint).first():
        return make_response_with_token({"message": "you can publish a post with the same name in one day"}, user.token), 409

    post_excerpt = post_text[:50]
    post = Post(name=post_name, published_date=published_date,
                text=post_text, excerpt=post_excerpt, endpoint=endpoint)

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
    return make_response_with_token({"message": "post added"}, user.token), 200


@app.route('/editpost', methods=["POST"])
def editpost():
    user = is_login(request, session)
    if not user:
        return make_response_with_token({"message": "unauthorized request"}, ""), 401
    try:
        content = request.json
        post_name = html.escape(content["post_name"])
        post_text = content["post_text"]
        post_id = content["post_id"]
    except:
        return make_response_with_token({"message": "post name or post body invalid"}, user.token), 400
    post = session.query(Post).filter_by(id=post_id).first()
    if post:
        if post.author.id != user.id:
            return make_response_with_token({"message": "unauthorized request"}, user.token), 401
        post.name = post_name
        post.text = post_text
        endpoint = f"/{post.published_date.year}/{post.published_date.month}/{post.published_date.day}/{'-'.join(post_name.split()).lower()}"
        if (p := session.query(Post).filter_by(endpoint=endpoint).first()) and p.id != post_id:
            return make_response_with_token({"message": "you can publish a post with the same name in one day"}, user.token), 409
        try:
            tags = set([session.query(Tag)
                        .filter_by(name=i['name']).first() for i in content['tags']])
            post.tags = list(tags)
        except:
            pass
        session.add(post)
        session.commit()
        return make_response_with_token({"message": "post updated"}, user.token), 200
    return make_response_with_token({"message": "post not found"}, user.token), 404


@app.route('/createtag', methods=["POST"])
def addtag():
    user = is_login(request, session)
    if not user:
        return make_response_with_token({"message": "unauthorized request"}, ""), 401
    try:
        content = request.json
        tag_name = content['tag_name']
    except:
        return make_response_with_token({"message": "tag name invalid"}, user.token), 400
    tag = session.query(Tag).filter(func.lower(Tag.name) == tag_name).first()
    if tag:
        return make_response_with_token({"message": "tag exist"}, user.token), 409
    tag = Tag(name=tag_name)
    session.add(tag)
    session.commit()
    return make_response_with_token({"message": "tag added"}, user.token), 200

# for custom pages like about or contact
@app.route('/<string:custom>', methods=["GET"])
def customPages(custom):
    user = is_login(request, session)
    page = session.query(CustomPage).filter_by(endpoint=f"/{custom}").first()
    if page:
        res = page.__dict__
        res.pop('_sa_instance_state', None)
        res.pop("id")
        res.pop("endpoint")
        if user:
            return make_response_with_token(res, user.token), 200
        return make_response_with_token(res, ""), 200
    if user:
        return make_response_with_token({"message": "page not found"}, user.token), 404
    return make_response_with_token({"message": "page not found"}, ""), 404


@app.route('/createcustompage', methods=["POST"])
def createCustomPage():
    user = is_login(request, session)
    if not user:
        return make_response_with_token({"message": "unauthorized request"}, ""), 401
    try:
        content = request.json
        page_name = html.escape(content["name"])
        page_text = content["text"]
        page_endpoint = content["endpoint"]
    except:
        return make_response_with_token({"message": "page name, text or endpoint invalid"}, user.token), 400
    page_exist = session.query(CustomPage).filter_by(
        endpoint=page_endpoint).first()
    if page_exist:
        return make_response_with_token({"message": "page exist"}, user.token), 409
    page = CustomPage(name=page_name, text=page_text, endpoint=page_endpoint)
    session.add(page)
    session.commit()
    return make_response_with_token({"message": "page added"}, user.token), 200


if __name__ == '__main__':
    app.run()
