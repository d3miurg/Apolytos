from database import base

import sqlalchemy


class Users_to_chats_relation(base):
    __tablename__ = 'users_to_chats_relations'
    user = sqlalchemy.Column(sqlalchemy.Integer,
                             sqlalchemy.ForeignKey('users.id'),
                             primary_key=True)
    chat = sqlalchemy.Column(sqlalchemy.Integer,
                             sqlalchemy.ForeignKey('chats.id'),
                             primary_key=True)
    user_relation = sqlalchemy.orm.relationship('User', back_populates='chats')
    chat_relation = sqlalchemy.orm.relationship('Chat', back_populates='users')


class User(base):
    __tablename__ = 'users'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    username = sqlalchemy.Column(sqlalchemy.String(32))
    password = sqlalchemy.Column(sqlalchemy.String(64))
    slug = sqlalchemy.Column(sqlalchemy.String(32))
    chats = sqlalchemy.orm.relationship('Users_to_chats_relation',
                                        back_populates='user_relation')
    messages = sqlalchemy.orm.relationship('Message')

    def __str__(self):
        return self.username


class Chat(base):
    __tablename__ = 'chats'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String(32))
    users = sqlalchemy.Column(sqlalchemy.Text,
                              sqlalchemy.ForeignKey('users.id'))
    slug = sqlalchemy.Column(sqlalchemy.String(32))
    users = sqlalchemy.orm.relationship('Users_to_chats_relation',
                                        back_populates='chat_relation')
    messages = sqlalchemy.orm.relationship('Message')

    def __str__(self):
        return self.slug


class Message(base):
    __tablename__ = 'messages'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    content = sqlalchemy.Column(sqlalchemy.String(2048))
    author = sqlalchemy.Column(sqlalchemy.Integer,
                               sqlalchemy.ForeignKey('users.id'))
    chat = sqlalchemy.Column(sqlalchemy.Integer,
                             sqlalchemy.ForeignKey('chats.id'))

    def __str__(self):
        return self.content
