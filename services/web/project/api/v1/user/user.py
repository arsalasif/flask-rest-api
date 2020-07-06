from flask import jsonify, Blueprint
from flask_accept import accept
from flask.views import MethodView

from ..base import BaseAPI
from ....models.user import User
from ...common.utils.helpers import register_api
from ...common.utils.exceptions import NotImplementedException
from ...common.utils.decorators import authenticate

user_blueprint = Blueprint('user', __name__)


class UserAPI(BaseAPI, MethodView):
    decorators = [accept('application/json'), authenticate]

    def post(self, logged_in_user_id: int, **kwargs):
        raise NotImplementedException()

    def get(self, logged_in_user_id: int, user_id: int = None, **kwargs):
        if user_id is None:
            user = User.get(logged_in_user_id)
            return jsonify(email=user.email, username=user.username, name=user.name, active=user.active,
                           created_at=user.created_at, social_id=user.social_id, social_type=user.social_type)
        else:
            raise NotImplementedException()

    def put(self, logged_in_user_id: int, user_id: int, **kwargs):
        raise NotImplementedException()

    def delete(self, logged_in_user_id: int, user_id: int, **kwargs):
        raise NotImplementedException()


register_api(blueprint=user_blueprint,
             view=UserAPI,
             endpoint='user_api',
             url='/user/',
             pk='user_id')
