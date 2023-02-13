from app import application
from flask import request

import json

# префиксы в именах переменных используются в основном для того, чтобы
# иметь в одном пространстве имён две одноимённые переменные
#
# d - dictionary
# f - file
# s - string


@application.route('/')
def index():
    return ''.join(['Главная страница пока не планируется.\n',
                    ' Обратитесь к администрации WinSy\n',
                    ' для получения карты сайта'])


@application.route('/register', methods=['GET', 'POST'])
def register():
    return 'Регистрация ещё не готова'
    d_requsest = request.json
    with open('whitelist.json', 'r') as f_whitelist:
        d_whitelist = json.load(f_whitelist)


@application.route('/login', methods=['GET', 'POST'])
def login():
    return 'Вход ещё не готов'
    d_requsest = request.json
    with open('whitelist.json', 'r') as f_whitelist:
        d_whitelist = json.load(f_whitelist)

    s_username = d_requsest['username']
    s_request_password = d_requsest['password']
    s_whitelist_password = d_whitelist[s_username]
    if s_whitelist_password != s_request_password:
        return 'Введён неверный пароль'
    else:
        return 'Вход выполнен'

@application.route('/chat')
def chatlist():
    return 'Список чатов ещё не готов'

@application.route('/chat/<slug>', methods=['GET', 'POST'])
def chat():
    return 'Чаты ещё не готовы'
    d_requsest = request.json
    with open('whitelist.json', 'r') as f_whitelist:
        d_whitelist = json.load(f_whitelist)



@application.errorhandler(404)
def page_not_found(e):
    print('Got json:', request.json)
    return ''.join(['Страница не найдена. Убедитесь, что:\n',
                    '1. Это не прикол\n',
                    '2. Адрес написан правильно\n',
                    '3. Если вы перешли сюда по гиперссылке, дайте по башке\n',
                    ' тому, кто её сделал']), 404


@application.errorhandler(400)
def bad_request(e):
    print('Got json:', request.json)
    return 'Возникла ошибка запроса со стороны клиента. Обратитесь к тому, кто такое посмел допустить. Если вы не уверены, кто это может быть, обратитесь к администрации WinSy c настолько подробным описанием проблемы, насколько вы можете себе позволить', 400
