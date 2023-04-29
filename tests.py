from defs import require_jwt
from app import application


def lost():
    pass


def missing_token():
    print('missing token test')
    result = require_jwt(lost)()
    print(result)


if __name__ == '__main__':
    with application.test_request_context():
        missing_token()
