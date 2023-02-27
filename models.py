from app import database


class Users_to_chats_relation(database.Model):
    __tablename__ = 'users_to_chats_relations'
    user = database.Column(database.Integer,
                           database.ForeignKey('users.id'),
                           primary_key=True)
    chat = database.Column(database.Integer,
                           database.ForeignKey('chats.id'),
                           primary_key=True)
    user_relation = database.relationship('User', back_populates='chats')
    chat_relation = database.relationship('Chat', back_populates='users')


class User(database.Model):
    __tablename__ = 'users'
    id = database.Column(database.Integer, primary_key=True) # возможно, стоит вынести в отдельный класс
    username = database.Column(database.String(32))
    password = database.Column(database.String(64))
    slug = database.Column(database.String(32)) # дублирование кода, вынести в отдельный класс
    chats = database.relationship('Users_to_chats_relation',
                                  back_populates='user_relation')

    def __str__(self):
        return self.username


class Chat(database.Model):
    __tablename__ = 'chats'
    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(32))
    users = database.Column(database.Text, database.ForeignKey("users.id"))
    slug = database.Column(database.String(32)) # дублирование
    users = database.relationship('Users_to_chats_relation',
                                  back_populates='chat_relation')

    def __str__(self):
        return self.slug

class Message(database.Model): # необходимы отношения
    __tablename__ = 'messages'
    id = database.Column(database.Integer, primary_key=True)
    content = database.Column(database.String(2048))
    author = database.Column(database.Integer)
    chat = database.Column(database.Integer)

    def __str__(self):
        return self.content
