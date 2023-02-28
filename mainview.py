from app import application
from app import database
from flask import request
from flask import jsonify
from flask import Response
from models import User
from models import Chat
from models import Message
from sqlalchemy import exc
from datetime import datetime
from time import sleep

import jwt

#import flask-script - 3
#import flask-jwt - 3
#import flask-restful - 3


# https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods
# https://ru.wikipedia.org/wiki/%D0%A1%D0%BF%D0%B8%D1%81%D0%BE%D0%BA_%D0%BA%D0%BE%D0%B4%D0%BE%D0%B2_%D1%81%D0%BE%D1%81%D1%82%D0%BE%D1%8F%D0%BD%D0%B8%D1%8F_HTTP

# просмотреть статус-коды - 3
messages_queue = [] # очередь может заполниться одинаковыми сообщениями # нужно отвязать очередь от сервера


def return_message():
    if messages_queue != []:
        yield jsonify({'message': messages_queue.pop(0)})
        sleep(.1)
    else:
        sleep(1)


@application.route('/')
def index():
    try:
        User.query.all()
        Chat.query.all()
        Message.query.all()
    except exc.InterfaceError:
        return jsonify({'status': '0',
                        'reason': 'database is down'})

    return jsonify({'status': '1',
                    'reason': 'api is active'})


@application.route('/register', methods=['POST'])
def register():
    json_request = request.json
    required_keys = ['username', 'password', 'slug']
    for key in required_keys:
        if key not in json_request:
            return jsonify({'status': '0',
                            'reason': f'{key} is not in request JSON'})

    if (len(json_request['password']) != 64):
        return jsonify({'status': '0',
                        'reason': 'password is not hashed'})
    new_user = User(username=json_request['username'],
                    password=json_request['password'],
                    slug=json_request['slug'])
    database.session.add(new_user)
    database.session.commit()
    return jsonify({'status': '1',
                    'reason': 'successful register'})


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
        return jsonify({'status': '0',
                        'reason': 'specify slug or username'})

    if not recieved_user:
        return jsonify({'status': '0',
                        'reason': 'user not found'})

    if (recieved_user.password != password):
        return jsonify({'status': '0',
                        'reason': 'invalid password'})

    current_time = datetime.now().timestamp()
    auth_expiration_date = current_time + application.config['AUTH_LIFETIME']
    refresh_expiration_date = current_time + application.config['REFRESH_LIFETIME']
    auth_token = jwt.encode({'id': recieved_user.id, 'exp': auth_expiration_date}, application.config['SECURE_KEY'])
    refresh_token = jwt.encode({'id': recieved_user.id, 'exp': refresh_expiration_date}, application.config['SECURE_KEY'])
    return jsonify({'status': '1',
                    'reason': 'successful login',
                    'auth_token': auth_token,
                    'refresh_token': refresh_token})


@application.route('/chats', methods=['GET']) #добавить создание чатов
def chatlist(): #сделать счётчик
    all_chats = Chat.query.all()
    chat_slugs = []
    for n in all_chats:
        chat_slugs.append(n.slug)

    return jsonify({'status': '1',
                    'reason': 'readed chat list from database',
                    'chatlist': chat_slugs})


@application.route('/chats/<slug>', methods=['GET', 'POST'])
def chat(slug):
    global messages_queue
    if (request.method == 'GET'):
        count = request.args.get('count') # может прийти строка
        last_messages = Message.query.order_by(Message.id.desc()).slice(0, int(count))
        last_messages_content = []
        for n in last_messages:
            last_messages_content.append(n.content)

        messages_queue += last_messages_content

        return Response(return_message(), content_type='text/event-stream')
        '''return jsonify({'status': '1',
                        'reason': 'returned messages',
                        'last_messages': last_messages_content})'''

    if (request.method == 'POST'):
        recieved_content = request.json['content'] # нужно проверить метод запроса и его тело - 2
        token_payload = jwt.decode(request.json['token'], application.config['SECURE_KEY'], algorithms=["HS256"])
        user_id = token_payload['id']
        current_chat = Chat.query.filter(Chat.slug == slug).first()
        new_message = Message(content=recieved_content, chat=current_chat.id, author=user_id)
        messages_queue.append(recieved_content)
        database.session.add(new_message)
        database.session.commit()

        return jsonify({'status': '1',
                        'reason': 'sended message to server'})

    return jsonify({'status': '0',
                    'reason': 'no action given'})


@application.route('/refresh', methods=['GET']) # починить токен - 1
def refresh_token():
    return jsonify({'status': '0',
                    'reason': 'not implemented'}), 501

    token = request.args.get('token')
    return jsonify({'status': '1',
                    'reason': 'sended message to server'})


# настройки чата
# форма создания нового чата
# референс апи
@application.errorhandler(400)
def bad_request(e):
    return 'Возникла ошибка запроса со стороны клиента. Обратитесь к тому, кто такое посмел допустить. Если вы не уверены, кто это может быть, обратитесь к администрации WinSy c настолько подробным описанием проблемы, насколько вы можете себе позволить', 400


@application.errorhandler(404)
def page_not_found(e):
    return ''.join(['Страница не найдена. Убедитесь, что:\n',
                    '1. Это не прикол\n',
                    '2. Адрес написан правильно\n',
                    '3. Если вы перешли сюда по гиперссылке, дайте по башке\n',
                    ' тому, кто её сделал']), 404


@application.errorhandler(405)
def method_not_allowed(e):
    return 'Неправильный метод', 405


if __name__ == '__main__':
    application.run()
