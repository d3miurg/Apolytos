from app import application
from app import database
from flask import request
from flask import jsonify
from models import Users
from models import Chats

# нужен полный рефакторинг под REST


@application.route('/')
def index():
    return jsonify({'status': '1',
                    'reason': 'api is active'})


@application.route('/register', methods=['GET', 'POST'])
def register():
    json_request = request.json
    new_user = Users(username=json_request['username'],
                     password=json_request['password'],
                     slug=json_request['username']) # проверить регистрацию # проверить правильность заполнения формы
    database.session.add(new_user) # убедиться, что база работает
    database.session.commit()
    return jsonify({'status': '1',
                    'reason': 'successful register'})


@application.route('/login', methods=['GET', 'POST'])
def login():
    json_request = request.json # нужно проверить метод запроса и его тело

    recieved_user = Users.query.filter(Users.username == json_request['username']).first() # может быть 2 пользователя с одним именем # пользователь может не существовать
    if recieved_user.password != json_request['password']:
        return jsonify({'status': '0',
                        'reason': 'invalid password'})

    return jsonify({'status': '1',
                    'reason': 'successful login'})


@application.route('/chat')
def chatlist():
    all_chats = Chats.query.all()
    chat_slugs = []
    for n in all_chats:
        chat_slugs.append(n.slug)

    return jsonify({'status': '1',
                    'reason': 'readed chat list from database',
                    'chatlist': chat_slugs})


@application.route('/chat/<slug>', methods=['GET', 'POST'])
def chat(slug):
    print(slug)

    return 'Чаты ещё не готовы'


@application.errorhandler(404)
def page_not_found(e):
    return ''.join(['Страница не найдена. Убедитесь, что:\n',
                    '1. Это не прикол\n',
                    '2. Адрес написан правильно\n',
                    '3. Если вы перешли сюда по гиперссылке, дайте по башке\n',
                    ' тому, кто её сделал']), 404


@application.errorhandler(400)
def bad_request(e):
    return 'Возникла ошибка запроса со стороны клиента. Обратитесь к тому, кто такое посмел допустить. Если вы не уверены, кто это может быть, обратитесь к администрации WinSy c настолько подробным описанием проблемы, насколько вы можете себе позволить', 400


if __name__ == '__main__':
    application.run()
