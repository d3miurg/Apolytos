from app import database


class Users(database.Model):
    id = database.Column(database.Integer, primary_key=True) # возможно, стоит вынести в отдельный класс
    username = database.Column(database.String(32))
    password = database.Column(database.String(64))
    slug = database.Column(database.String(32)) # дублирование кода, вынести в отдельный класс


class Chats(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(32))
    users = database.Column(database.Text)
    slug = database.Column(database.String(32)) # дублирование


class Messages(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    content = database.Column(database.String(2048))
    author = database.Column(database.Integer)
    chat = database.Column(database.Integer)
