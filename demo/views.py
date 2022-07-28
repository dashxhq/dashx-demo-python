import datetime
import os
from datetime import timezone

import bcrypt as bcrypt
from dashx_python import client as dashx
import jwt
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
        user_data = {'firstName': user['first_name'], 'lastName': user['last_name'], 'email': user['email']}
        dashx.client.identify(user['id'], user_data)
        dashx.client.track('User Registered', user['id'], user_data)
        return make_response(jsonify({'message': 'User created.'}), 201)
    except sqlalchemy_exc.IntegrityError as e:
        return make_response(jsonify({'message': 'User already exists.'}), 409)
    except Exception as e:
        response = {'message': 'Internal Server Error.'}
        return make_response(jsonify(response), 500)


@app.route('/forgot-password', methods=['POST'])
def forgot_password():
    req_body = request.get_json()
    if 'email' not in req_body:
        return make_response(jsonify({'message': 'Email is required.'}), 400)

    email = req_body.get('email')
    try:
        with db_engine.connect() as conn:
            user_rs = conn.execute('SELECT * FROM users WHERE email = %s', email)
            user = user_rs.fetchone()

        if len(user) == 0:
            return make_response(jsonify({'message': 'This email does not exist in our records.'}), 404)

        token = jwt.encode(
            {"exp": datetime.datetime.now(tz=timezone.utc) + datetime.timedelta(seconds=900), 'email': email},
            os.environ.get('JWT_SECRET'), algorithm="HS256"
        )

        dashx.client.deliver('email/forgot-password', {
            'to': email,
            'data': {'token': token.decode('ascii')}
        })

        return make_response(jsonify({'message': 'Check your inbox for a link to reset your password.'}), 200)

    except Exception as e:
        return make_response(jsonify({'message': str(e)}), 500)
