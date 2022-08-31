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


@app.route('/reset-password', methods=['POST'])
def reset_password():
    req_body = request.get_json()
    if 'token' not in req_body:
        return make_response(jsonify({'message': 'Token is required.'}), 400)

    if 'password' not in req_body:
        return make_response(jsonify({'message': 'Password is required.'}), 400)

    token = req_body.get('token')
    password = req_body.get('password')

    try:
        decoded_token = jwt.decode(token, os.environ.get('JWT_SECRET'), algorithms=['HS256'])
        email = decoded_token.get('email')

        salt = bcrypt.gensalt()
        encrypted_password = bcrypt.hashpw(password.encode('utf-8'), salt)

        with db_engine.connect() as conn:
            rs = conn.execute('UPDATE users SET encrypted_password = %s WHERE email = %s RETURNING id',
                              encrypted_password.decode('ascii'), email)
            user = rs.fetchone()

        if len(user) == 0:
            return make_response(jsonify({'message': 'Invalid reset password link.'}), 422)

        return make_response(jsonify({'message': 'You have successfully reset your password.'}), 200)

    except jwt.exceptions.ExpiredSignatureError as e:
        return make_response(jsonify({'message': 'Your reset password link has expired.'}), 422)

    except Exception as e:
        return make_response(jsonify({'message': str(e)}), 500)


@app.route('/contact', methods=['POST'])
def contact():
    req_body = request.get_json()
    if 'name' not in req_body or\
            'email' not in req_body or\
            'feedback' not in req_body:
        return make_response(jsonify({'message': 'All fields are required.'}), 422)
    name = req_body.get('name')
    email = req_body.get('email')
    feedback = req_body.get('feedback')

    try:
        dashx.client.deliver('email', {
          'content': {
            'name': 'Contact us',
            'from': 'noreply@dashxdemo.com',
            'to': [email, 'sales@dashx.com'],
            'subject': 'Contact Us Form',
            'html_body': '''<mjml>
                <mj-body>
                  <mj-section>
                    <mj-column>
                      <mj-divider border-color="#F45E43"></mj-divider>
                      <mj-text>Thanks for reaching out! We will get back to you soon!</mj-text>
                      <mj-text>Your feedback: </mj-text>
                      <mj-text>Name: {name}</mj-text>
                      <mj-text>Email: {email}</mj-text>
                      <mj-text>Feedback: {feedback}</mj-text>
                      <mj-divider border-color="#F45E43"></mj-divider>
                    </mj-column>
                  </mj-section>
                </mj-body>
              </mjml>'''.format(name=name, email=email, feedback=feedback)
          }
        })

        return make_response(jsonify({'message': 'Thanks for reaching out! We will get back to you soon.'}), 200)
    except:
        return make_response(jsonify({'message': 'Internal Server Error.'}), 500)


@app.route('/login', methods=['POST'])
def login():
    req_body = request.get_json()
    if 'email' not in req_body or\
            'password' not in req_body:
        return make_response(jsonify({'message': 'Incorrect email or password.'}), 401)
    email = req_body.get('email')
    password = req_body.get('password')

    try:
        with db_engine.connect() as conn:
            user_rs = conn.execute('SELECT * FROM users WHERE email = %s', email)
            user = user_rs.fetchone()

        if len(user) == 0:
            return make_response(jsonify({'message': 'Incorrect email or password.'}), 401)

        if not bcrypt.checkpw(password.encode('utf-8'), user['encrypted_password'].encode('utf-8')):
            return make_response(jsonify({'message': 'Incorrect email or password.'}), 401)

        token = jwt.encode(
            {"exp": datetime.datetime.now(tz=timezone.utc) + datetime.timedelta(seconds=86400*30),
             'id': user['id'], 'email': user['email'], 'first_name': user['first_name'],
             'last_name': user['last_name'],
             'dashx_token': dashx.client.generateIdentityToken(user['id'])},
            os.environ.get('JWT_SECRET'), algorithm="HS256"
        )

        return make_response(jsonify({'message': 'User logged in.', 'token': token.decode('ascii')}), 200)

    except Exception as e:
        return make_response(jsonify({'message': str(e)}), 500)
