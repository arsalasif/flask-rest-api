from flask import request, current_app, jsonify, Blueprint
from flask_accept import accept
from sqlalchemy import exc
from pydantic import ValidationError

from .... import bcrypt, db
from ....api.common.utils.exceptions import InvalidPayloadException, NotFoundException, \
    ServerErrorException, ValidationException
from ....api.common.utils.decorators import authenticate, privileges
from ....models.user import User, UserRole
from ....api.common.utils.helpers import session_scope
from ..validations.auth.core import UserRegister, UserLogin, PasswordChange, PasswordReset, PasswordRecovery


auth_core_blueprint = Blueprint('auth_core', __name__)


@auth_core_blueprint.route('/auth/register', methods=['POST'])
@accept('application/json')
def register_user():
    """
    New user registration
    """
    # Get post data
    post_data = request.get_json()
    if not post_data:
        raise InvalidPayloadException()
    try:
        data = UserRegister(**post_data)
    except ValidationError as e:
        raise ValidationException(e)

    # Check for existing user
    try:
        user = User(**data.dict())
        with session_scope(db.session) as session:
            session.add(user)

        with session_scope(db.session) as session:
            token = user.encode_email_token()
            user.email_token_hash = bcrypt.generate_password_hash(token, current_app.config.get(
                'BCRYPT_LOG_ROUNDS')).decode()

        if not current_app.testing:
            from ....api.common.utils.mails import send_registration_email
            send_registration_email(user, token.decode())

        # Generate auth token
        auth_token = user.encode_auth_token()
        return jsonify(message='Successfully registered.', auth_token=auth_token.decode()), 201
    except (exc.IntegrityError, Exception):
        session.rollback()
        raise ServerErrorException()


@auth_core_blueprint.route('/auth/login', methods=['POST'])
@accept('application/json')
def login_user():
    """
    User login
    """
    post_data = request.get_json()
    if not post_data:
        raise InvalidPayloadException()

    try:
        data = UserLogin(**post_data)
    except ValidationError as e:
        raise ValidationException(e)

    user = User.first_by(email=data.email)
    if not user:
        raise NotFoundException(message='User does not exist.')

    if bcrypt.check_password_hash(user.password, data.password):
        auth_token = user.encode_auth_token()
        return jsonify(message='Successfully logged in.', auth_token=auth_token.decode())
    else:
        raise InvalidPayloadException(message="Incorrect password.")


@auth_core_blueprint.route('/auth/logout', methods=['GET'])
@accept('application/json')
@privileges(role=UserRole.USER | UserRole.ADMIN)
def logout_user(_):
    """
    Logout user
    """
    return jsonify(message='Successfully logged out.')


@auth_core_blueprint.route('/auth/status', methods=['GET'])
@accept('application/json')
@authenticate
def get_user_status(user_id: int):
    """
    Get authentication status
    """
    user = User.get(user_id)
    return jsonify(email=user.email, username=user.username, name=user.name, active=user.active,
                   created_at=user.created_at)


@auth_core_blueprint.route('/auth/password_change', methods=['PUT'])
@accept('application/json')
@authenticate
def password_change(user_id: int):
    """
    Changes user password when logged in
    """
    post_data = request.get_json()
    if not post_data:
        raise InvalidPayloadException()
    user = User.get(user_id)
    try:
        data = PasswordChange(user=user, **post_data)
    except ValidationError as e:
        raise ValidationException(e)

    with session_scope(db.session):
        user.password = bcrypt.generate_password_hash(data.new_password,
                                                      current_app.config.get('BCRYPT_LOG_ROUNDS')).decode()

    return jsonify(message='Successfully changed password.')


@auth_core_blueprint.route('/auth/password_reset', methods=['PUT'])
@accept('application/json')
def password_reset():
    """
    Reset user password
    """
    post_data = request.get_json()
    if not post_data:
        raise InvalidPayloadException()

    data = PasswordReset(**post_data)
    user_id = User.decode_password_token(data.token)
    user = User.get(user_id)
    if not user or not user.token_hash or not bcrypt.check_password_hash(user.token_hash, data.token):
        raise InvalidPayloadException('Invalid password reset token. Please try again.')

    with session_scope(db.session):
        user.password = bcrypt.generate_password_hash(data.password,
                                                      current_app.config.get('BCRYPT_LOG_ROUNDS')).decode()
        user.token_hash = None
    return jsonify(message='Successfully reset password.')


@auth_core_blueprint.route('/auth/password_recovery', methods=['POST'])
@accept('application/json')
def password_recovery():
    """
    Creates a password_recovery_hash and sends email to user
    """
    post_data = request.get_json()
    if not post_data:
        raise InvalidPayloadException()

    try:
        data = PasswordRecovery(**post_data)
    except ValidationError as e:
        raise ValidationException(e)

    user = User.first_by(email=data.email)
    if user:
        token = user.encode_password_token()
        with session_scope(db.session):
            user.token_hash = bcrypt.generate_password_hash(token, current_app.config.get('BCRYPT_LOG_ROUNDS')).decode()
        if not current_app.testing:
            from project.api.common.utils.mails import send_password_recovery_email
            send_password_recovery_email(user, token.decode())  # send recovery email
        return jsonify(message='Password recovery email sent.')
    else:
        raise NotFoundException("Email does not exist.")
