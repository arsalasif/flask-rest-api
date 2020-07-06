from flask import Blueprint
from flask.views import MethodView
from flask_accept import accept

from ..base import BaseAPI
from ....models.user import User, UserRole
from ...common.utils.helpers import register_api
from ...common.utils.decorators import privileges
from ..validations.admin.users import UsersPost, UsersPut

users_blueprint = Blueprint('users', __name__)


class UsersAPI(BaseAPI, MethodView):
    decorators = [accept('application/json'), privileges(role=UserRole.ADMIN)]

    def post(self, logged_in_user_id: int, **kwargs):
        return super().post(logged_in_user_id, UsersPost, User)

    def get(self, logged_in_user_id: int, user_id: int = None, **kwargs):
        if user_id is None:
            return super().get(logged_in_user_id, User)
        else:
            return super().get_by_id(logged_in_user_id, user_id, User)

    def put(self, logged_in_user_id: int, user_id: int, **kwargs):
        return super().put(logged_in_user_id, user_id, UsersPut, User)

    def delete(self, logged_in_user_id: int, user_id: int, **kwargs):
        return super().delete(logged_in_user_id, user_id, User)


register_api(blueprint=users_blueprint,
             view=UsersAPI,
             endpoint='users_api',
             url='/users/',
             pk='user_id')
