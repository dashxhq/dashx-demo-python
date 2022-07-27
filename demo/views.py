import bcrypt as bcrypt
from dashx_python import client as dashx
import sqlalchemy.exc as sqlalchemy_exc
from flask import request, jsonify, make_response

from demo import app, db_engine


@app.route('/register', methods=['POST'])
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
    encrypted_password = bcrypt.hashpw(password.encode('utf-8'), salt)

    try:
        with db_engine.connect() as conn:
            rs = conn.execute('INSERT INTO users (first_name, last_name, email, encrypted_password) '
                              'VALUES (%s, %s, %s, %s) RETURNING *', first_name, last_name, email,
                              encrypted_password.decode('ascii'))
            user = rs.fetchone()
        user_data = {'first_name': user['first_name'], 'last_name': user['last_name'], 'email': user['email']}
        dashx.client.identify(user['id'], user_data)
        dashx.client.track('User Registered', user['id'], user_data)
        return make_response(jsonify({'message': 'User created.'}), 201)
    except sqlalchemy_exc.IntegrityError as e:
        return make_response(jsonify({'message': 'User already exists.'}), 409)
    except Exception as e:
        response = {'message': 'Internal Server Error.'}
        return make_response(jsonify(response), 500)
