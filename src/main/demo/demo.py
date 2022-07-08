from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:postgres@localhost/demo"
db = SQLAlchemy(app)


if __name__ == "__main__":
    from views import *
    app.run()
"""
curl --location --request POST 'http://127.0.0.1:5000/register/' --header 'Content-Type: application/json' --data-raw '{ "first_name": "Vikrant", "last_name": "Vishwakarma", "email": "vikrant.vishwakarma07@gmail.com", "password": "9591297013" }'
"""