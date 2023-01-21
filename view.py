from app import app
from flask import request

import json

# префиксы в именах переменных используются в основном для того, чтобы
# иметь в одном пространстве имён две одноимённые переменные, но так же
# помогает различать их типы
#
# d - dictionary
# f - file
# s - string


@app.route('/')
def index():
    return 'It\'s working. Now try to use API'


@app.route('/login', methods=['GET', 'POST'])
def login():
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
    


@app.errorhandler(404)
def page_not_found(e):
    return 'Страница не найдена. Убедитесь, что:\n1. Это не прикол\n2. Адрес написан правильно\n3. Если вы перешли сюда по гиперссылке, дайте по башке тому, кто её сделал', 404


@app.errorhandler(400)
def bad_request(e):
    return 'Возникла ошибка запроса со стороны клиента. Обратитесь к тому, кто такое посмел допустить. Если вы не уверены, кто это может быть, обратитесь к администрации WinSy c настолько подробным описанием проблемы, насколько вы можете себе позволить', 400
