import os
import re
import secrets

database_url = "sqlite:///myblog.db?check_same_thread=False"


def create_config():
    with open("config.py", "w") as f:
        secret = secrets.token_urlsafe(32)

        db = f"database_url = '{database_url}'\n"
        ppp = "posts_per_page = 3\n"
        sc = f"SECRET_KEY = '{secret}'"

        f.write(db + ppp + sc)


def install():
    files = os.listdir()

    if "config.py" in files:
        print("!!!attention!!!")
        print("you may lose your author passwords")
        print("there is already a config file.")
        print("do you want to recreate the config? [y/n] ", end="")
        choice = input()
        if choice == "y":
            create_config()
    else:
        create_config()

    import config
    from models import create_database

    if "myblog.db" in files:
        print("!!!attention!!!")
        print("you may lose your all posts and authors")
        print("there is already a database.")
        print("do you want to recreate the database? [y/n] ", end="")
        choice = input()
        if choice == "y":
            create_database(database_url)
    else:
        create_database(database_url)

    choice = input("do you want to create a new user? [y/n] ")
    if choice == "y":
        from auth import input_user
        input_user()


if __name__ == "__main__":
    install()
