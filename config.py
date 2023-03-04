class Configuration(object):
    DEBUG = True
    THREADED = True
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root@localhost/winsy'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECURE_KEY = 'debugkey'
    AUTH_LIFETIME = 72000
    REFRESH_LIFETIME = 7776000
