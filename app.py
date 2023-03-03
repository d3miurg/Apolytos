from fastapi import FastAPI
from fastapi import Request
from fastapi import Body
from fastapi import WebSocket
from fastapi.responses import JSONResponse
from starlette.websockets import WebSocketDisconnect
from sqlalchemy import exc
from datetime import datetime
from config import server_configuration
from config import jwt_configuration
from models import User
from models import Chat
from models import Message
from database import session
from websocket_instance import ConnectionManager

import uvicorn
import jwt

# в пизду идёт эта документация, если для её составления нужно выёбываться
application = FastAPI()
websocket_manager = ConnectionManager()


@application.get('/')
def index():
    try:
        session().query(User).first()
        session().query(Chat).first()
        session().query(Message).first()
    except exc.InterfaceError:
        return JSONResponse(content={'error': 1,
                                     'reason': 'database is down'},
                            status_code=503)

    return JSONResponse(content={'error': 0,
                                 'reason': 'API is active'},
                        status_code=200)


@application.get('/teapod')
def teapod(request: Request):
    coffee_type = request.query_params.get('coffee')
    print(coffee_type)
    if not coffee_type:
        return JSONResponse(content={'error': 1,
                                     'reason': 'specify coffee type',
                                     'additional': 'latte, americano and espresso is available'},
                            status_code=418)
    elif coffee_type == 'tea':
        return JSONResponse(content={'error': 1,
                                     'reason': 'only coffee',
                                     'additional': 'latte, americano and espresso is available'},
                            status_code=406)
    available_coffee_types = ['latte', 'americano', 'espresso']
    if coffee_type not in available_coffee_types:
        return JSONResponse(content={'error': 1,
                                     'reason': 'this type is not available',
                                     'additional': 'latte, americano and espresso is available'},
                            status_code=406)
    return JSONResponse(content={'error': 0,
                                 'reason': 'making coffee for you, come back later'},
                        status_code=200)


@application.get('/login')
def login(request: Request):
    username = request.query_params.get('username')
    password = request.query_params.get('password') # пароль может не прийти - 3
    slug = request.query_params.get('slug')
    if slug:
        print('slug')
        recieved_user = session().query(User).filter(User.slug == slug).first()
        print(recieved_user)
    elif username:
        print('username')
        recieved_user = session().query(User).filter(User.username == username).first()
        print(recieved_user)
    else:
        return JSONResponse(content={'error': 1,
                                     'reason': 'specify slug or username'},
                            status_code=400)

    if not recieved_user:
        return JSONResponse(content={'error': 1,
                                     'reason': 'user not found'},
                            status_code=401)

    elif (recieved_user.password != password):
        return JSONResponse(content={'error': 1,
                                     'reason': 'invalid password'},
                            status_code=401)

    current_time = datetime.now().timestamp()
    auth_expiration_date = current_time + jwt_configuration['auth_lifetime']
    refresh_expiration_date = current_time + jwt_configuration['refresh_lifetime']
    auth_token = jwt.encode({'id': recieved_user.id, 'exp': auth_expiration_date}, jwt_configuration['secure_key'])
    refresh_token = jwt.encode({'id': recieved_user.id, 'exp': refresh_expiration_date}, jwt_configuration['secure_key'])
    return JSONResponse(content={'error': 0,
                                 'reason': 'successful login',
                                 'auth_token': auth_token,
                                 'refresh_token': refresh_token},
                        status_code=200)


@application.post("/register")
def register(request_body=Body()):
    username = request_body.get('username')
    password = request_body.get('password')
    slug = request_body.get('slug')
    if len(password) != 64:
        return JSONResponse(content={'error': 1,
                                     'reason': 'password is not hashed'},
                            status_code=400)

    new_user = User(username=username,
                    password=password,
                    slug=slug)

    add_session = session()
    add_session.add(new_user)
    add_session.commit()
    del add_session

    return JSONResponse(content={'error': 0,
                                 'reason': 'successful register'},
                        status_code=201)


@application.get('/chats')
def chat_list():
    all_chats = session().query(Chat).all()
    chat_slugs = [n.slug for n in all_chats]
    return JSONResponse(content={'error': 0,
                                 'reason': 'readed chat list from database',
                                 'chatlist': chat_slugs},
                        status_code=200)


@application.websocket('/chats/{slug}')
async def chat_socket(slug: str, socket: WebSocket):
    print(socket)
    print(websocket_manager)

    await websocket_manager.add_connection(socket)
    try:
        while True:
            data = await socket.receive_text()
            await websocket_manager.broadcast(data)

    except WebSocketDisconnect:
        websocket_manager.discard_connection(socket)
    '''return JSONResponse(content={'error': 1,
                                 'reason': 'not implemented'},
                        status_code=501)'''


if __name__ == '__main__':
    uvicorn.run('app:application', **server_configuration)
