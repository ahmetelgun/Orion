# Orion
### Simple blog api with flask and SQLAlchemy

Orion is a simple blog api for your personal usage. You can create, edit, and delete your posts, manage with tags.

# Installation

```bash
git clone https://github.com/ahmetelgun/Orion.git
cd Orion
# (Optional) create and activate new virtualenv. For virtualenv, see https://www.geeksforgeeks.org/python-virtual-environment/
pip install -r requirements.txt
python install.py
```
# Run

```bash
python3 app.py
```

For deployment, see https://flask.palletsprojects.com/en/1.1.x/deploying/

# Enpoints

| Endpoint                                                            | Methods | Short description              |
| :------------------------------------------------------------------ | :------ | :----------------------------- |
| [/posts](#poststagstringtag_namepageintpage_number)                 | GET     | returns post list              |
| [/\<year\>/\<month\>/\<day\>/\<post-name\>](#yearmonthdaypost-name) | GET     | returns post text and tags     |
| [/createpost](#createpost)                                          | POST    | create post with given tags    |
| [/editpost](#editpost)                                              | POST    | edit published post            |
| [/taglist](#taglist)                                                | GET     | return all tags                |
| [/createtag](#createtag)                                            | POST    | create new tag                 |
| [/\<custom-page-endpoint\>](#custom-page-endpoint)                  | GET     | see custom page                |
| [/createcustompage](#createcustompage)                              | POST    | create custom page. e.g. About |
| [/login](#login)                                                    | POST    | Author login                   |
| [/logout](#logout)                                                  | POST    | Author logout                  |


## /posts[?tag=\<string:tag_name\>&page=\<int:page_number\>]

Returns post list. Supports searching by page number or tag name.

**Allowed methods:**
* GET

**Optional queries:**
* tag
* page

**successful response:**

```yaml
{   
    "current_page": "int:current_page_number",
    "total_number_of_page": "int:total_page",
    "posts" :[
        "author": "string:author-name",
        "endpoint": "string:/yyyy/mm/dd/post-name",
        "excerpt": "string:post-excerpt",
        "name": "string:Post name",
        "published_date": "string:dd.mm.yyyy",
        "tags": [
            "string:tag_name",
            "string:tag_name"
        ]   
    ] 
}
``` 

### Optional queries

- tag: Returns posts that has given tag. Tag name query must be case sensitive, complete and encoded. For example tag name 'C Plus Plus', query must be 'tag=C%20Plus%20Plus'. If given tag is not exist, returns 404.

- page: Returns posts in given page. If this query not in request, returns first page as default. Setting number of posts per page is changable from configs fileWhen given page number is not exist or invalid, first page.

> page and tag query can be used together.


## /\<year\>/\<month\>/\<day\>/\<post-name\>

Returns selected post. 

**Allowed methods:**
* GET

**successful response:**

```yaml
{
    "endpoint": "string:/yyyy/mm/dd/postname",
    "name": "string:post_name",
    "published_date": "string:dd.mm.yyyy",
    "tags": [
        "string:tag_name",
        "string:tag_name"
    ],
    "text": "string:post_text"
}
```

If post not found, returns 404.


## /createpost

Create new post

**Allowed methods:**
* POST

**Optioanal parameters**
* tags

**Request body template**
```yaml
{
    "post_name": "string:post_name",
    "post_text": "string:post_text",
    "tags": [
        "name": "string:tag_name",
        "name": "string:tag_name"
    ]
}
```

User authentication explained [here](#user-authentication).

post_name and post_text are required. Tags optioanal. If the tags parameter is not sent, no one tag added. If one of the tags in the request is not exist, that tag is not added to post. If request does not contains post_name or post_text data, returns 400.

If you try create 2 post with same name in same day, returns 409.

## /editpost

Edit the text, name or tags of a post with given post_id.

**Allowed methods**
* POST

**Optioanal parameters:**
* tags

**Request body template**

```yaml
{
    "post_name": "string:post_name",
    "post_text": "string:post_text",
    "post_id": "int:post_id",
    "tags": [
        "name": "string:tag_name",
        "name": "string:tag_name"
    ]
}
```

User authentication explained [here](#user-authentication).

If you don't want change post name or post text, send current values. If you want add or remove tags, append new tags to old tags or remove tags from old list. If you dont't want change tags, don't send tags parameter. To remove all tags from post, send emty tags list.

post_name, post_text and post_id are required. If one of them is not exist in the request, returns 400.

If you change a post's name and a post exist in same day with same name, returns 400.

If post_id not found, returns 404.

## /taglist 

Get all tags 

**Allowed methods**
* GET

**successful response:**

```yaml
[
    "string:tag_name",
    "string:tag_name",
    "string:tag_name"
]
```

## /createtag 

**Allowed methods**
* POST

**Request body template**

```yaml
{
    "tag_name": "string:tag_name"
}
```

User authentication explained [here](#user-authentication).

If tag_name parameter is not exist in request, returns 400.

If tag exists, returns 409.

## /\<custom-page-endpoint\> 

Get a custom page like About or Contact 

**Allowed methods**
* GET

If page not found, return 404.

Successful response:

```yaml
{
    "name": "string:name",
    "text": "string:text"
}
```

## /createcustompage  

Get a custom page like About or Contact 

**Allowed methods**
* POST

**Request body template**
```yaml
{
    "name": "string:page_name",
    "text": "string:page_text",
    "endpoint": "string:/page_endpoint",
}
```

User authentication explained [here](#user-authentication).

enpoint must contains only one path. /foo/bar not allowed.

If name, text or endpoint not exist, returns 400.

If enpoint exist, returns 409.

When custom page successfuly created, returns 200.

## /login

User login endpoint

**Allowed methods**
* POST

**Request body template**
```yaml
{
    "username": "string:page_name",
    "password": "string:page_text"
}

```

If username or password not exist in request, returns 400

If username or password incorrect, returns 401

If username and password are correct, isLogin cookie is set to true, token cookie is set to JWT token and returns 200.

## /logout

**Allowed methods**
* POST

logout has no any body content. 

If user not logged in, returns 404.

If logout successfuly, isLogin cookie is set to false, token cookie is set to empty and returns 200.

# User authentication

Orion use JWT for user authentication. When an user login to system, Orion set a JWT token as cookie. This cookie is httponly, this means you don't access token from JavaScript. When user login, Orion set isLogin. If user logged in, isLogin cookie is true, otherwise cookie is false. 

Token expire after 24 hour. When token's expiration time less than 12 hour, token recreated. 

Token deletes after expire.

When user go to /logout endpoint, token deletes from database and set to empty cookie.

