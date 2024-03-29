from flask import request
from flask import jsonify
from flask import Blueprint
from app import database
from app import sockets
from models import Chat
from models import Users_to_chats_relation
from models import Message
from models import User
from defs import require_jwt
from defs import check_requirements

chats_blueprint = Blueprint('chats', __name__)


@chats_blueprint.route('/', methods=['GET'], endpoint='chatlist')
def chatlist():
    all_chats = Chat.query.all()

    chat_list = [{'name': n.name,
                  'slug': n.slug,
                  'last_message': {'author': n.messages[-1].author,
                                   'content': n.messages[-1].content}
                  if len(n.messages) > 0 else []}
                 for n in all_chats]
    return jsonify({'error': 0,
                    'reason': 'readed chat list from database',
                    'chatlist': chat_list}), 200


@chats_blueprint.route('/', methods=['POST'], endpoint='create_chat')
@require_jwt
@check_requirements(required_keys=['name', 'slug'])
def create_chat():
    name = request.json.get('name')
    slug = request.json.get('slug')
    admin_id = request.json.get('user_id')
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


@chats_blueprint.route('/', methods=['PUT'], endpoint='enter_chat')
@require_jwt
@check_requirements(required_keys=['slug'])
def enter_chat():
    slug = request.json.get('slug')
    user_id = request.json.get('user_id')
    target_chat = Chat.query.filter(Chat.slug == slug).first()
    new_relation = Users_to_chats_relation(user=user_id,
                                           chat=target_chat.id,
                                           is_admin=False)
    database.session.add(new_relation)
    database.session.commit()
    return jsonify({'error': 0,
                    'reason': 'joined chat'}), 202


@chats_blueprint.route('/<slug>', methods=['GET'], endpoint='chat')
@check_requirements(required_keys=['count'])
def chat(slug):
    count = int(request.args.get('count'))
    last_messages = Chat.query.filter(Chat.slug == slug).first().messages[-1:-count:-1]

    message_list = [{'content': n.content,
                     'author': n.author_relation.username}
                    for n in last_messages]

    return jsonify({'error': 0,
                    'reason': 'returned messages',
                    'last_messages': message_list}), 200


@chats_blueprint.route('/<slug>', methods=['POST'], endpoint='send_message')
@require_jwt
@check_requirements(required_keys=['content'])
def send_message(slug):
    recieved_content = request.json.get('content')

    if not recieved_content:
        return jsonify({'error': 0,
                        'reason': 'sended message to server'}), 400
    user_id = request.json.get('user_id')

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
        return jsonify({'error': 21,
                        'reason': 'can\'t send message in view mode',
                        'additional': 'enter chat to send message'}), 403


@chats_blueprint.route('/<slug>', methods=['DELETE'], endpoint='leave_chat')
@require_jwt
@check_requirements(required_keys=['user_slug'])
def leave_chat(slug):
    relation_table = Users_to_chats_relation
    user_to_leave_slug = request.json.get('user_slug')
    user_id = request.json.get('user_id')
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
        return jsonify({'error': 21,
                        'reason': 'you can\'t do that'}), 200


@sockets.on('echo')
def echo(data):
    with open('echo.txt', 'w') as openfile:
        openfile.write(data)
