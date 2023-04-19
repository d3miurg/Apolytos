from flask import jsonify
from flask import Blueprint
from flask import abort
from models import User

users_blueprint = Blueprint('users', __name__)


@users_blueprint.route('/<slug>', endpoint='get_profile')
def get_profile(slug):
    recieved_user = User.query.filter(User.slug == slug).first()
    if not recieved_user:
        abort(404)

    # Наверное нужно будет брать около 100 комментариев, и остальные подгружать
    user_info = {'id': recieved_user.id,
                 'username': recieved_user.username,
                 'slug': recieved_user.slug,
                 'status': recieved_user.status,
                 'comments': [{'content': comm.content,
                               'author': comm.author}
                              for comm in recieved_user.comments]}

    return jsonify({'error': '0',
                    'reason': 'got information about the user',
                    'info': user_info})
