from auth import input_user
import config
from models import create_database
import secrets
import re
create_database(config.database_url)
print("database created")

input_user()

def create_secret(is_exist):
    secret = secrets.token_urlsafe(32)
    with open("config.py", "r") as f:
        configs = f.read()
        if is_exist:
            configs = re.sub(r"SECRET_KEY.*", f"SECRET_KEY = '{secret}'", configs)
        else:
            configs += f"SECRET_KEY = '{secret}'"
    with open("config.py", "w") as f:
        f.write(configs)
try:
    config.SECRET_KEY
    renew = input("do you want to renew secrets? you will lose your passwords. [y/n]")
    if renew == "y":
        create_secret(True)
except:
    create_secret(False)