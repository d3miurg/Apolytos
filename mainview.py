from app import application
from app import database
from flask import request
from flask import jsonify
from models import User
from models import Chat
from models import Message
from models import Users_to_chats_relation
from sqlalchemy import exc
from datetime import datetime

import jwt
# https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods
# https://ru.wikipedia.org/wiki/%D0%A1%D0%BF%D0%B8%D1%81%D0%BE%D0%BA_%D0%BA%D0%BE%D0%B4%D0%BE%D0%B2_%D1%81%D0%BE%D1%81%D1%82%D0%BE%D1%8F%D0%BD%D0%B8%D1%8F_HTTP
# https://ru.wikipedia.org/wiki/%D0%A1%D0%BF%D0%B8%D1%81%D0%BE%D0%BA_MIME-%D1%82%D0%B8%D0%BF%D0%BE%D0%B2


def require_jwt(function):
    def _wrapper(*args, **kwargs):
        token = request.json.get('token')
        if not token:
            return jsonify({'error': 1,
                            'reason': 'token is required'}), 403
        try:
            payload = jwt.decode(token,
                                 application.config['SECURE_KEY'],
                                 algorithms=["HS256"])
            expiration_timestamp = payload.get('exp')
            password = payload.get('password')
            user_id = payload.get('id')
        except jwt.exceptions.DecodeError:
            return jsonify({'error': 1,
                            'reason': 'invalid token'}), 403
        except jwt.exceptions.ExpiredSignatureError:
            return jsonify({'error': 1,
                            'reason': 'token expired'}), 403

        if not user_id:
            return jsonify({'error': 1,
                            'reason': 'empty token'}), 403

        if password and not request.base_url.endswith('/refresh'):
            return jsonify({'error': 1,
                            'reason': 'refresh token given as auth'}), 403

        if not isinstance(expiration_timestamp, float):
            reason = 'token doesn\'t have exipration date'
            return jsonify({'error': 1,
                            'reason': reason}), 403

        responce = function(*args, **kwargs)
        return responce

    return _wrapper


def check_requirements(required_keys):
    def check_constructor(function):
        def _wrapper(*args, **kwargs):
            request_keys = request.args
            if request.method != 'GET':
                request_keys = request.json
            value_list = [request_keys.get(key) for key in required_keys]
            key_value_dict = dict(zip(value_list, required_keys))
            if None in value_list:
                reason = f'key "{key_value_dict[None]}" is required'
                return jsonify({'error': 1,
                                'reason': reason}), 400

            responce = function(*args, **kwargs)
            return responce

        return _wrapper

    return check_constructor


def create_tokens(user):
    appconfig = application.config
    timestamp = datetime.now().timestamp()
    auth_expiration_timestamp = timestamp + appconfig['AUTH_LIFETIME']
    refresh_expiration_timestamp = timestamp + appconfig['REFRESH_LIFETIME']

    auth_token = jwt.encode({'id': user.id,
                             'exp': auth_expiration_timestamp},
                            appconfig['SECURE_KEY'])
    refresh_token = jwt.encode({'id': user.id,
                                'password': user.password,
                                'exp': refresh_expiration_timestamp},
                               appconfig['SECURE_KEY'])

    return auth_token, refresh_token


@application.route('/', endpoint='index')
def index():
    try:
        User.query.all()
        Chat.query.all()
        Message.query.all()
    except exc.InterfaceError:
        return jsonify({'error': 1,
                        'reason': 'database is down'}), 503

    return jsonify({'error': 0,
                    'reason': 'api is active',
                    'version': '0.2.8.0',
                    'stack': ['Python 3.10.1',
                              'Flask 2.2.2',
                              'InnoDB 5.7.27-30']}), 200


@application.route('/teapod', methods=['GET'], endpoint='teapod')
@check_requirements(required_keys=['coffee'])
def teapod():
    additional = {'additional': 'latte, americano and espresso is available'}
    coffee_type = request.args.get('coffee')
    if coffee_type == 'tea':
        return jsonify({'error': 1,
                        'reason': 'only coffee'} | additional), 406
    elif coffee_type == 'coffee':
        return jsonify({'coffee': 'coffee',
                        'coffee coffee': 'coffee',
                        'coffee coffee coffee': 'coffee'}), 418

    available_coffee_types = ['latte', 'americano', 'espresso']
    if coffee_type not in available_coffee_types:
        return jsonify({'error': 1,
                        'reason': 'cannot make this type'} | additional), 406

    normal_reason = 'making coffee for you, come back later'
    return jsonify({'error': 0,
                    'reason': normal_reason}), 200


@application.route('/auth', methods=['POST'], endpoint='register')
@check_requirements(required_keys=['username', 'password', 'slug'])
def register():
    username = request.json.get('username')
    password = request.json.get('password')
    slug = request.json.get('slug')

    if len(password) != 64:
        return jsonify({'error': 1,
                        'reason': 'invalid password type',
                        'additional': 'SHA256 hexdigest is recommended'}), 400

    new_user = User(username=username,
                    password=password,
                    slug=slug)
    database.session.add(new_user)
    database.session.commit()
    return jsonify({'error': 0,
                    'reason': 'successful register'}), 201


@application.route('/auth', methods=['GET'], endpoint='login')
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
            return jsonify({'error': 1,
                            'reason': 'specify slug',
                            'found_slugs': user_slugs}), 400
        elif not recieved_user:
            return jsonify({'error': 1,
                            'reason': 'user not found'}), 401
        else:
            recieved_user = found_users[0]
    else:
        return jsonify({'error': 1,
                        'reason': 'specify slug or username'}), 400

    if recieved_user.status == 'sus':
        return jsonify({'error': 1,
                        'reason': 'this account suspended'}), 403

    if (recieved_user.password != password):
        return jsonify({'error': 1,
                        'reason': 'invalid password'}), 401

    auth_token, refresh_token = create_tokens(recieved_user)

    return jsonify({'error': 0,
                    'reason': 'successful login',
                    'auth_token': auth_token,
                    'refresh_token': refresh_token}), 200


@application.route('/chats', methods=['GET'], endpoint='chatlist')
def chatlist():
    all_chats = Chat.query.all()
    chat_slugs = [n.slug for n in all_chats]

    return jsonify({'error': 0,
                    'reason': 'readed chat list from database',
                    'chatlist': chat_slugs}), 200


@application.route('/chats', methods=['POST'], endpoint='create_chat')
@require_jwt
@check_requirements(required_keys=['name', 'slug'])
def create_chat():
    name = request.json.get('name')
    slug = request.json.get('slug')
    token_payload = jwt.decode(request.json['token'],
                               application.config['SECURE_KEY'],
                               algorithms=["HS256"])
    admin_id = token_payload['id']
    new_chat = Chat(name=name, slug=slug)
    database.session.add(new_chat)
    database.session.commit()
    new_relation = Users_to_chats_relation(user=admin_id,
                                           chat=new_chat.id,
                                           is_admin=True)
    database.session.add(new_relation)
    database.session.commit()
    return jsonify({'error': 0,
                    'reason': 'created chat'}), 201


@application.route('/chats', methods=['PUT'], endpoint='enter_chat')
@require_jwt
@check_requirements(required_keys=['slug'])
def enter_chat():
    slug = request.json.get('slug')
    token_payload = jwt.decode(request.json['token'],
                               application.config['SECURE_KEY'],
                               algorithms=["HS256"])
    user_id = token_payload['id']
    target_chat = Chat.query.filter(Chat.slug == slug).first()
    new_relation = Users_to_chats_relation(user=user_id,
                                           chat=target_chat.id,
                                           is_admin=False)
    database.session.add(new_relation)
    database.session.commit()
    return jsonify({'error': 0,
                    'reason': 'joined chat'}), 202


@application.route('/chats/<slug>', methods=['GET'], endpoint='chat')
@check_requirements(required_keys=['count'])
def chat(slug):
    count = request.args.get('count')
    if isinstance(count, int):
        return jsonify({'error': 1,
                        'reason': 'specify count of messages'}), 400

    last_messages = Chat.query.filter(Chat.slug == slug).first().messages

    message_list = [{'content': n.content,
                     'author': n.author_relation.username}
                    for n in last_messages]

    return jsonify({'error': 0,
                    'reason': 'returned messages',
                    'last_messages': message_list}), 200


@application.route('/chats/<slug>', methods=['POST'], endpoint='send_message')
@require_jwt
@check_requirements(required_keys=['content'])
def send_message(slug):
    recieved_content = request.json.get('content')

    if not recieved_content:
        return jsonify({'error': 0,
                        'reason': 'sended message to server'}), 400
    token_payload = jwt.decode(request.json['token'],
                               application.config['SECURE_KEY'],
                               algorithms=['HS256'])
    user_id = token_payload['id']

    current_chat = Chat.query.filter(Chat.slug == slug).first()

    relation_user = Users_to_chats_relation.user
    relation_chat = Users_to_chats_relation.chat

    raw_relation = Users_to_chats_relation.query
    user_relation = raw_relation.filter(relation_user == user_id)
    chat_relation = user_relation.filter(relation_chat == current_chat.id)
    filtered_relation = chat_relation.first()

    print(dir(current_chat.users))
    print(current_chat.users)
    print(filtered_relation)

    if filtered_relation in current_chat.users:
        new_message = Message(content=recieved_content,
                              chat=current_chat.id,
                              author=user_id)
        database.session.add(new_message)
        database.session.commit()

        return jsonify({'error': 0,
                        'reason': 'sended message to server'}), 201

    else:
        return jsonify({'error': 1,
                        'reason': 'can\'t send message in view mode',
                        'additional': 'enter chat to send message'}), 403


@application.route('/chats/<slug>', methods=['DELETE'], endpoint='leave_chat')
@require_jwt
@check_requirements(required_keys=['user_slug'])
def leave_chat(slug):
    relation_table = Users_to_chats_relation
    user_to_leave_slug = request.json.get('user_slug')
    token = request.json.get('token')
    token_payload = jwt.decode(token,
                               application.config['SECURE_KEY'],
                               algorithms=['HS256'])
    user_id = token_payload.get('id')
    current_chat = Chat.query.filter(Chat.slug == slug).first()
    query_user = User.query.filter(User.slug == user_to_leave_slug).first()
    relation = relation_table.query
    chat_relation = relation.filter(relation_table.chat == current_chat.id)
    user_relation = chat_relation.filter(relation_table.user == query_user.id)
    admin_relation = chat_relation.filter(relation_table.user == user_id)
    user_entry = user_relation.first()
    admin_entry = admin_relation.first()
    if (user_id == user_entry.user) or (user_id == admin_entry.user):
        user_relation.delete()
        database.session.commit()

        return jsonify({'error': 0,
                        'reason': 'removed user from chat'}), 200

    else:
        return jsonify({'error': 1,
                        'reason': 'you can\'t do that'}), 200


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
        return jsonify({'error': 1,
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
def internal_serve_error(e):
    return jsonify({'error': 1,
                    'reason': 'server is down'}), 405


# сообщества
# посты
if __name__ == '__main__':
    application.run()
