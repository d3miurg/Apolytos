from app import application
from flask import request
from flask import jsonify
from sqlalchemy import exc
from models import User
from models import Chat
from models import Message
from models import Comment
from defs import require_jwt
from defs import check_requirements
from defs import create_tokens
from blueprints.auth import auth_blueprint
from blueprints.chats import chats_blueprint
from blueprints.users import users_blueprint

import jwt
# https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods
# https://ru.wikipedia.org/wiki/%D0%A1%D0%BF%D0%B8%D1%81%D0%BE%D0%BA_%D0%BA%D0%BE%D0%B4%D0%BE%D0%B2_%D1%81%D0%BE%D1%81%D1%82%D0%BE%D1%8F%D0%BD%D0%B8%D1%8F_HTTP
# https://ru.wikipedia.org/wiki/%D0%A1%D0%BF%D0%B8%D1%81%D0%BE%D0%BA_MIME-%D1%82%D0%B8%D0%BF%D0%BE%D0%B2


@application.route('/', methods=['GET'], endpoint='index')
def index():
    try:
        User.query.first()
        Chat.query.first()
        Message.query.first()
        Comment.query.first()
    except exc.InterfaceError:
        return jsonify({'error': '01',
                        'reason': 'database is down'}), 503

    return jsonify({'error': 0,
                    'reason': 'api is active',
                    'version': '0.3.1.1',
                    'stack': {'Python': '3.10.1',
                              'Flask': '2.2.2',
                              'InnoDB': '5.7.27-30',
                              'SQLAlchemy': '2.0.4'}}), 200


@application.route('/teapod', methods=['GET'], endpoint='teapod')
@check_requirements(required_keys=['coffee'])
def teapod():
    additional = {'additional': 'latte, americano and espresso is available'}
    coffee_type = request.args.get('coffee')
    if coffee_type == 'tea':
        return jsonify({'error': '02',
                        'reason': 'only coffee'} | additional), 406
    elif coffee_type == 'coffee':
        return jsonify({'coffee': 'coffee',
                        'coffee coffee': 'coffee',
                        'coffee coffee coffee': 'coffee'}), 418

    available_coffee_types = ['latte', 'americano', 'espresso']
    if coffee_type not in available_coffee_types:
        return jsonify({'error': '03',
                        'reason': 'cannot make this type'} | additional), 406

    normal_reason = 'making coffee for you, come back later'
    return jsonify({'error': 0,
                    'reason': normal_reason}), 200


@application.route('/refresh',
                   methods=['PATCH', 'POST'],
                   endpoint='refresh_token')
@require_jwt
def refresh_token():
    token = request.json.get('token')
    payload = jwt.decode(token,
                         application.config['SECURE_KEY'],
                         algorithms=['HS256'])

    user_id = payload.get('id')
    password = payload.get('password')

    user = User.query.filter(User.id == user_id).first()

    if user.password != password:
        return jsonify({'error': 41,
                        'reason': 'invalid token',
                        'additional': 'server don\'t recieve fake tokens'})

    auth_token, refresh_token = create_tokens(user)
    return jsonify({'error': 0,
                    'reason': 'refreshed',
                    'auth_token': auth_token,
                    'refresh_token': refresh_token}), 200


@application.errorhandler(400)
def bad_request(e):
    additional = 'check "Content-Type" header and body spelling'
    return jsonify({'error': 1,
                    'reason': 'bad request',
                    'additional': additional}), 400


@application.errorhandler(404)
def page_not_found(e):
    return jsonify({'error': 1,
                    'reason': 'page not found'}), 404


@application.errorhandler(405)
def method_not_allowed(e):
    return jsonify({'error': 1,
                    'reason': 'invalid method'}), 405


@application.errorhandler(500)
def internal_server_error(e):
    return jsonify({'error': 1,
                    'reason': 'server is down'}), 500


application.register_blueprint(auth_blueprint, url_prefix='/auth')
application.register_blueprint(chats_blueprint, url_prefix='/chats')
application.register_blueprint(users_blueprint, url_prefix='/users')

if __name__ == '__main__':
    application.run()
