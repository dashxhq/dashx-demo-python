from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:postgres@localhost/demo"
db = SQLAlchemy(app)


if __name__ == "__main__":
    app.run()
