from flask import request
from flask import jsonify
from flask import Blueprint
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

    if (recieved_user.password != password):
        return jsonify({'error': 15,
                        'reason': 'invalid password'}), 401

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

    if len(password) != 64:
        return jsonify({'error': 16,
                        'reason': 'invalid password type',
                        'additional': 'SHA256 hexdigest is recommended'}), 400

    new_user = User(username=username,
                    password=password,
                    slug=slug)
    database.session.add(new_user)
    database.session.commit()
    return jsonify({'error': 0,
                    'reason': 'successful register'}), 201
