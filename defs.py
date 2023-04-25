from flask import request
from flask import jsonify
from datetime import datetime
from app import application

import jwt


def require_jwt(function):
    def _wrapper(*args, **kwargs):
        token = request.json.get('token')
        if not token:
            return jsonify({'error': 1,
                            'reason': 'token is required'}), 403
        try:
            payload = jwt.decode(token,
                                 application.config['SECURE_KEY'],
                                 algorithms=["HS256"])
            expiration_timestamp = payload.get('exp')
            password = payload.get('password')
            user_id = payload.get('id')
        except jwt.exceptions.DecodeError:
            return jsonify({'error': 1,
                            'reason': 'invalid token'}), 403
        except jwt.exceptions.ExpiredSignatureError:
            return jsonify({'error': 1,
                            'reason': 'token expired'}), 403

        if not user_id:
            return jsonify({'error': 1,
                            'reason': 'empty token'}), 403

        if password and not request.base_url.endswith('/refresh'):
            return jsonify({'error': 1,
                            'reason': 'refresh token given as auth'}), 403

        if not isinstance(expiration_timestamp, float):
            reason = 'token doesn\'t have exipration date'
            return jsonify({'error': 1,
                            'reason': reason}), 403

        request.json['user_id'] = user_id
        responce = function(*args, **kwargs)
        return responce

    return _wrapper


def check_requirements(required_keys):
    def check_constructor(function):
        def _wrapper(*args, **kwargs):
            request_keys = request.args
            if request.method != 'GET':
                request_keys = request.json
            value_list = [request_keys.get(key) for key in required_keys]
            key_value_dict = dict(zip(value_list, required_keys))
            if None in value_list:
                reason = f'key "{key_value_dict[None]}" is required'
                return jsonify({'error': 1,
                                'reason': reason}), 400

            responce = function(*args, **kwargs)
            return responce

        return _wrapper

    return check_constructor


def create_tokens(user):
    appconfig = application.config
    timestamp = datetime.now().timestamp()
    auth_expiration_timestamp = timestamp + appconfig['AUTH_LIFETIME']
    refresh_expiration_timestamp = timestamp + appconfig['REFRESH_LIFETIME']

    auth_token = jwt.encode({'id': user.id,
                             'exp': auth_expiration_timestamp},
                            appconfig['SECURE_KEY'])
    refresh_token = jwt.encode({'id': user.id,
                                'password': user.password,
                                'exp': refresh_expiration_timestamp},
                               appconfig['SECURE_KEY'])

    return auth_token, refresh_token
