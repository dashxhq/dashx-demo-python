import os

from flask import Flask
from sqlalchemy import create_engine

app = Flask(__name__)
connection_string = 'postgresql://{user}:{passwd}@{host}/{database}'
try:
    pg_passwd = os.environ['PG_PASSWORD']
    pg_host = os.environ['PG_HOST']
    pg_user = os.environ['PG_USER']
    pg_database = os.environ['PG_DATABASE']
    db_engine = create_engine(connection_string.format(user=pg_user, passwd=pg_passwd, host=pg_host, database=pg_database))
except KeyError as e:
    print("Expecting environment variable " + str(e))


if __name__ == "__main__":
    from views import *
    app.run()
    app.url_map.strict_slashes = False
"""
curl --location --request POST 'http://127.0.0.1:5000/register/' --header 'Content-Type: application/json' --data-raw '{ "first_name": "Vikrant", "last_name": "Vishwakarma", "email": "vikrant.vishwakarma07@gmail.com", "password": "9591297013" }'
"""