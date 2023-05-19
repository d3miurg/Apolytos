from flask import request
from flask import jsonify
from flask import Blueprint
from hashlib import sha256
from argon2 import PasswordHasher
from argon2 import exceptions as argon2exceptions
from models import User
from app import database
from defs import check_requirements
from defs import create_tokens

auth_blueprint = Blueprint('auth', __name__)


@auth_blueprint.route('/', methods=['GET'], endpoint='login')
@check_requirements(required_keys=['password'])
def login():
    username = request.args.get('username')
    password = request.args.get('password')
    slug = request.args.get('slug')
    if slug:
        recieved_user = User.query.filter(User.slug == slug).first()
    elif username:
        found_users = User.query.filter(User.username == username).all()
        if len(found_users) > 1:
            user_slugs = [n.slug for n in found_users]
            return jsonify({'error': 11,
                            'reason': 'specify slug',
                            'found_slugs': user_slugs}), 400
        elif not found_users:
            return jsonify({'error': 12,
                            'reason': 'user not found'}), 401
        else:
            recieved_user = found_users[0]
    else:
        return jsonify({'error': 13,
                        'reason': 'specify slug or username'}), 400

    if recieved_user.status == 'sus':
        return jsonify({'error': 14,
                        'reason': 'this account suspended'}), 403

    hasher = PasswordHasher()

    try:
        hasher.verify(recieved_user.password, password)

    except argon2exceptions.VerifyMismatchError:
        return jsonify({'error': 15,
                        'reason': 'invalid password'}), 401

    except argon2exceptions.InvalidHash:
        return jsonify({'error': 16,
                        'reason': 'password invalid for new safety policy',
                        'additional': 'change your password via /auth/'})

    auth_token, refresh_token = create_tokens(recieved_user)

    return jsonify({'error': 0,
                    'reason': 'successful login',
                    'auth_token': auth_token,
                    'refresh_token': refresh_token}), 200


@auth_blueprint.route('/', methods=['POST'], endpoint='register')
@check_requirements(required_keys=['username', 'password', 'slug'])
def register():
    username = request.json.get('username')
    password = request.json.get('password')
    slug = request.json.get('slug')

    hasher = PasswordHasher()
    password_hash = hasher.hash(password)

    new_user = User(username=username,
                    password=password_hash,
                    slug=slug)
    database.session.add(new_user)
    database.session.commit()
    return jsonify({'error': 0,
                    'reason': 'successful register'}), 201
