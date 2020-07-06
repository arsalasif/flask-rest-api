from flask import request, current_app
from functools import wraps

from ....api.common.utils.exceptions import UnauthorizedException, ForbiddenException
from ....models.user import User, UserRole


def privileges(role):
    """
    Decorator to verify user privileges based on active status and role
    (implicit authentication, no need to use authenticate decorator with privileges)
    """
    def actual_decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                raise UnauthorizedException()
            auth_token = auth_header.split(" ")[1]
            user_id = User.decode_auth_token(auth_token)
            user = User.get(user_id)
            if not user or not user.active:
                raise UnauthorizedException()
            user_role = UserRole(user.role)
            if not bool(user_role & role):
                raise ForbiddenException()
            return f(user_id, *args, **kwargs)
        return decorated_function
    return actual_decorator


def authenticate(f):
    """
    Decorator to authenticate users based on token
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            raise UnauthorizedException()
        auth_token = auth_header.split(" ")[1]
        user_id = User.decode_auth_token(auth_token)
        user = User.get(user_id)
        if not user or not user.active:
            raise UnauthorizedException()
        return f(user_id, *args, **kwargs)
    return decorated_function
