from app import application
from app import database
from flask import request
from flask import jsonify
from models import User
from models import Chat
from models import Message
from sqlalchemy import exc
from datetime import datetime

import jwt
# https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods
# https://ru.wikipedia.org/wiki/%D0%A1%D0%BF%D0%B8%D1%81%D0%BE%D0%BA_%D0%BA%D0%BE%D0%B4%D0%BE%D0%B2_%D1%81%D0%BE%D1%81%D1%82%D0%BE%D1%8F%D0%BD%D0%B8%D1%8F_HTTP

# придумать что-то с ответами

@application.route('/', methods=['GET'])
def index():
    try:
        User.query.all()
        Chat.query.all()
        Message.query.all()
    except exc.InterfaceError:
        return jsonify({'error': 1,
                        'reason': 'database is down'}), 503

    return jsonify({'error': 0,
                    'reason': 'api is active'}), 200


@application.route('/teapod', methods=['GET'])
def teapod():
    extra = {'additional': 'latte, americano and espresso is available'}
    coffee_type = request.args.get('coffee')
    if not coffee_type:
        return jsonify({'error': 1,
                        'reason': 'specify coffee type'}.update(extra)), 418
    elif coffee_type == 'tea':
        return jsonify({'error': 1,
                        'reason': 'only coffee'}.update(extra)), 406

    available_coffee_types = ['latte', 'americano', 'espresso']
    if coffee_type not in available_coffee_types:
        return jsonify({'error': 1,
                        'reason': 'cannot make this type'}.update(extra)), 406

    normal_reason = 'making coffee for you, come back later'
    return jsonify({'error': 0,
                    'reason': normal_reason}.update(extra)), 200


@application.route('/register', methods=['POST'])
def register():
    username = request.json.get('username')
    password = request.json.get('password')
    slug = request.json.get('slug')
    if (len(password) != 64):
        return jsonify({'error': 1,
                        'reason': 'invalid password type',
                        'additional': 'SHA256 hexdigest is recommended'}), 400

    if None in (username, slug):
        return jsonify({'error': 1,
                        'reason': 'incomplete form',
                        'additional': 'check for "username" and "slug"'}), 400

    new_user = User(username=username,
                    password=password,
                    slug=slug)
    database.session.add(new_user)
    database.session.commit()
    return jsonify({'error': 0,
                    'reason': 'successful register'}), 201


@application.route('/login', methods=['GET'])
def login():
    username = request.args.get('username')
    password = request.args.get('password')
    slug = request.args.get('slug')
    if slug:
        recieved_user = User.query.filter(User.slug == slug).first()
    elif username:
        found_users = User.query.filter(User.username == username).all()
        if len(found_users) > 1:
            user_slugs = [n.slug for n in found_users] # высокая вложенность
            return jsonify({'error': 1,
                            'reason': 'specify slug',
                            'found_slugs': user_slugs}), 400
    else:
        return jsonify({'error': 1,
                        'reason': 'specify slug or username'}), 400

    if not recieved_user:
        return jsonify({'error': 1,
                        'reason': 'user not found'}), 401

    if (recieved_user.password != password):
        return jsonify({'error': 1,
                        'reason': 'invalid password'}), 401

    current_time = datetime.now().timestamp()
    auth_expiration_date = current_time + application.config['AUTH_LIFETIME']
    refresh_expiration_date = current_time + application.config['REFRESH_LIFETIME']
    auth_token = jwt.encode({'id': recieved_user.id, 'exp': auth_expiration_date}, application.config['SECURE_KEY'])
    refresh_token = jwt.encode({'id': recieved_user.id, 'exp': refresh_expiration_date}, application.config['SECURE_KEY'])
    return jsonify({'error': 0,
                    'reason': 'successful login',
                    'auth_token': auth_token,
                    'refresh_token': refresh_token}), 200


@application.route('/chats', methods=['GET']) #добавить создание чатов # добавить вход в чат
def chatlist():
    all_chats = Chat.query.all()
    chat_slugs = [n.slug for n in all_chats]

    return jsonify({'error': 0,
                    'reason': 'readed chat list from database',
                    'chatlist': chat_slugs}), 200


@application.route('/chats/<slug>', methods=['GET']) # проверка на спам
def chat(slug):
    count = request.args.get('count')
    if isinstance(count, int):
        return jsonify({'error': 1,
                        'reason': 'specify count of messages'}), 400

    last_messages = Message.query.order_by(Message.id.desc()).slice(0, count)
    last_messages_content = [n.content for n in all_chats]

    return jsonify({'error': 0,
                    'reason': 'returned messages',
                    'last_messages': last_messages_content}), 200


@application.route('/chats/<slug>', methods=['POST'])
def send_message(slug):
    recieved_content = request.json['content'] # нужно проверить метод запроса и его тело - 2
    token_payload = jwt.decode(request.json['token'], application.config['SECURE_KEY'], algorithms=["HS256"])
    user_id = token_payload['id']
    current_chat = Chat.query.filter(Chat.slug == slug).first()
    new_message = Message(content=recieved_content, chat=current_chat.id, author=user_id)
    database.session.add(new_message)
    database.session.commit()

    return jsonify({'error': '1',
                    'reason': 'sended message to server'}), 201


@application.route('/refresh', methods=['GET']) # починить токен - 1
def refresh_token():
    return jsonify({'error': 1,
                    'reason': 'not implemented'}), 501

    token = request.args.get('token')
    return jsonify({'error': 0,
                    'reason': 'sended message to server'})


# настройки чата
# форма создания нового чата
# референс апи
# редактирование профиля
@application.errorhandler(400)
def bad_request(e):
    return jsonify({'error': '0',
                    'reason': 'bad request'}), 400


@application.errorhandler(404)
def page_not_found(e):
    return jsonify({'error': '0',
                    'reason': 'page not found'}), 404


@application.errorhandler(405)
def method_not_allowed(e):
    return jsonify({'error': '0',
                    'reason': 'invalid method'}), 405


@application.errorhandler(500)
def internal_serve_error(e):
    return jsonify({'error': '0',
                    'reason': 'server is down'}), 405


if __name__ == '__main__':
    application.run()
