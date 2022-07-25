import bcrypt as bcrypt
# from dashx_python import client as dashx
from flask import request, jsonify, make_response

from demo import app, db_engine


@app.route('/register', methods=["POST"])
def register():
    req_body = request.get_json()
    if 'first_name' not in req_body or\
            'last_name' not in req_body or\
            'email' not in req_body or\
            'password' not in req_body:
        return make_response(jsonify({'message': 'All fields are required.'}), 422)
    first_name = req_body.get('first_name')
    last_name = req_body.get('last_name')
    email = req_body.get('email')
    password = req_body.get('password')

    salt = bcrypt.gensalt()
    encrypted_password = bcrypt.hashpw(password.encode("utf-8"), salt)

    try:
        with db_engine.connect() as conn:
            rs = conn.execute('SELECT * FROM users')

            for row in rs:
                print(row)
            return make_response(jsonify({'status': 'success'}), 200)
        dashx.client.identify(first_name, last_name, email)
        dashx.client.track('User Registered', {"first_name": first_name, "last_name": last_name, "email": email})
    # except OperationalError as e:
    #     response = {'message': 'Internal Server Error.'}
    #     return make_response(jsonify(response), 500)
    except Exception as e:
        response = {'message': 'User already exists.'}
        return make_response(jsonify(response), 409)

    response = {"message": "User created."}
    return make_response(jsonify(response), 201)
    # if bcrypt.checkpw(password, encrypted_password):
    #     print("match")
    # else:
    #     print("does not match")
