from sqlalchemy.exc import IntegrityError

from demo import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100))
    email = db.Column(db.String(200), unique=True)
    password = db.Column(db.String(200), unique=True)

    def __init__(self, first_name, last_name, email, password):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password


def register_user(first_name, last_name, email, encrypted_password):
    try:
        new_user = User(first_name, last_name, email, encrypted_password)
        db.session.add(new_user)
        db.session.commit()
    except IntegrityError as e:
        print("Exception Occurred when adding User data")
        raise Exception("User already exist")
    except Exception as e:
        print("Exception Occurred when adding User data")
        raise Exception("Can't add user data")


if __name__ == "__main__":
    print("Creating database tables...")
    db.create_all()
    print("Done!")
