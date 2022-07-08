import bcrypt as bcrypt
from flask import request, jsonify, make_response
from flask_expects_json import expects_json

from src.main.demo.demo import app
from src.main.demo.model import register_user
from src.main.demo.schema import REGISTER_SCHEMA


@app.route('/register', methods=["POST"])
@expects_json(REGISTER_SCHEMA)
def register():
    print("register API called")
    req_body = request.get_json()
    first_name = req_body.get('first_name')
    last_name = req_body.get('last_name')
    email = req_body.get('email')
    password = req_body.get('password')

    salt = bcrypt.gensalt()
    encrypted_password = bcrypt.hashpw(password.encode("utf-8"), salt)

    try:
        register_user(first_name, last_name, email, encrypted_password)
    except Exception as e:
        response = {"message": str(e)}
        return make_response(jsonify(response), 409)

    response = {"message": "User created"}
    return make_response(jsonify(response), 201)
    # if bcrypt.checkpw(password, encrypted_password):
    #     print("match")
    # else:
    #     print("does not match")
