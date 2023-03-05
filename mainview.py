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


def construct_responce(error, reason, **additional):
    responce = {'error': error,
                'reason': reason}
    responce.update(additional)
    return responce


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
    additional = {'additional': 'latte, americano and espresso is available'}
    coffee_type = request.args.get('coffee')
    if not coffee_type:
        responce = construct_responce(1, 'specify coffee type', **additional)  # дублирование кода
        return jsonify(responce), 418
    elif coffee_type == 'tea':
        responce = construct_responce(1, 'only coffee', **additional) # дублирование кода
        return jsonify(responce), 406
    available_coffee_types = ['latte', 'americano', 'espresso']
    if coffee_type not in available_coffee_types:
        responce = construct_responce(1,
                                      'this type is not available',
                                      **additional) # дублирование кода
        return jsonify(responce), 406

    responce = construct_responce(0, 'making coffee for you, come back later') # дублирование кода
    return jsonify(responce), 200

@application.route('/register', methods=['POST'])
def register():
    required_keys = ['username', 'password', 'slug']
    for key in required_keys:
        if key not in request.json:
            return jsonify({'error': 1,
                            'reason': f'{key} is not in request JSON'}), 400

    username = request.json['username']
    password = request.json['password']
    slug = request.json['slug']
    if (len(password) != 64):
        return jsonify({'error': 1,
                        'reason': 'password is not hashed'}), 400
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
    password = request.args.get('password') # пароль может не прийти - 3
    slug = request.args.get('slug')
    print(slug)
    recieved_user = User.query.filter(User.slug == slug).first()
    if slug:
        print('slug')
        recieved_user = User.query.filter(User.slug == slug).first()
        print(recieved_user)
    elif username:
        print('username')
        recieved_user = User.query.filter(User.username == username).first() # может быть 2 пользователя с одним именем - 0 # # дубляж кода - 3
        print(recieved_user)
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
    chat_slugs = []
    for n in all_chats:
        chat_slugs.append(n.slug)

    return jsonify({'error': 0,
                    'reason': 'readed chat list from database',
                    'chatlist': chat_slugs}), 200


@application.route('/chats/<slug>', methods=['GET'])
def chat(slug):
    count = request.args.get('count')
    if isinstance(count, int):
        return jsonify({'error': 1,
                        'reason': 'specify count of messages'}), 400

    last_messages = Message.query.order_by(Message.id.desc()).slice(0, count)
    last_messages_content = []
    for n in last_messages:
        last_messages_content.append(n.content)

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
