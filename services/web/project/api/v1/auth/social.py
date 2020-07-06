from flask import request, current_app, redirect, jsonify, make_response, Blueprint
from sqlalchemy import and_
from flask_accept import accept
import requests
import json

from .... import bcrypt, db
from ....models.user import User, SocialAuth
from ....api.common.utils.helpers import session_scope
from ....api.common.utils.exceptions import BadRequestException, InvalidPayloadException, NotFoundException
from ....api.common.utils.decorators import authenticate
from uuid import uuid4

auth_social_blueprint = Blueprint('auth_social', __name__)


@auth_social_blueprint.route('/auth/github/login', methods=['GET'])
def github_login():
    """
    Logs in user using GitHub redirect to callback
    """
    authorization_endpoint = 'https://github.com/login/oauth/authorize'
    request_uri = current_app.github_client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + '/callback',
        scope=['user:email']
    )
    return redirect(request_uri)


@auth_social_blueprint.route('/auth/github/login/callback', methods=['GET'])
def github_login_callback():
    """
    Get access token with code and return the corresponding JWT
    """
    code = request.args.get("code")
    token_endpoint = 'https://github.com/login/oauth/access_token'

    # Prepare and send a request to get tokens
    token_url, headers, body = current_app.github_client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    headers['Accept'] = 'application/json'
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(current_app.config['GITHUB_CLIENT_ID'], current_app.config['GITHUB_CLIENT_SECRET'])
    )

    # Parse the tokens!
    current_app.github_client.parse_request_body_response(json.dumps(token_response.json()))

    user_endpoint = 'https://api.github.com/user'
    uri, headers, body = current_app.github_client.add_token(user_endpoint)
    github_response = requests.get(uri, headers=headers, data=body)

    # You want to make sure their email is verified.
    # The user authenticated with GitHub, authorized our
    # app, and now their email is verified through GitHub

    if 'login' in github_response.json():
        username = github_response.json()["login"]
        social_id = str(github_response.json()["id"])
        name = github_response.json()["name"]
        access_token = token_response.json()['access_token']
        email = github_response.json()["email"]

        if not email:
            email_endpoint = 'https://api.github.com/user/emails'
            uri, headers, body = current_app.github_client.add_token(email_endpoint)
            email_response = requests.get(uri, headers=headers, data=body)
            for github_emails in email_response.json():
                if github_emails['email'] and github_emails['primary'] is True:
                    email = github_emails['email']
                    break

        return add_user_into_db(email, name, username, social_id, access_token, SocialAuth.GITHUB)
    else:
        raise BadRequestException(message=f'Something went wrong with {SocialAuth.GITHUB.value}. Try again.')


@auth_social_blueprint.route('/auth/facebook/login', methods=['GET'])
def facebook_login():
    """
    Logs in user using Facebook redirect to callback
    """
    authorization_endpoint = 'https://www.facebook.com/v7.0/dialog/oauth'
    request_uri = current_app.facebook_client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + '/callback',
        scope=['email'],
        state=str(uuid4())
    )
    return redirect(request_uri)


@auth_social_blueprint.route('/auth/facebook/login/callback', methods=['GET'])
def facebook_login_callback():
    """
    Get access token with code and return the corresponding JWT
    """
    code = request.args.get("code")
    token_endpoint = 'https://graph.facebook.com/oauth/access_token'

    # Prepare and send a request to get tokens
    token_url, headers, body = current_app.facebook_client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    headers['Accept'] = 'application/json'
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(current_app.config['FACEBOOK_CLIENT_ID'], current_app.config['FACEBOOK_CLIENT_SECRET'])
    )

    # Parse the tokens!
    current_app.facebook_client.parse_request_body_response(json.dumps(token_response.json()))

    user_endpoint = 'https://graph.facebook.com/v7.0/me?fields=id,email,name'
    uri, headers, body = current_app.facebook_client.add_token(user_endpoint)
    facebook_response = requests.get(uri, headers=headers, data=body)

    # You want to make sure their email is verified.
    # The user authenticated with Facebook, authorized our
    # app, and now their email is verified through Facebook

    if 'email' in facebook_response.json():
        username = facebook_response.json()["email"]
        social_id = str(facebook_response.json()["id"])
        name = facebook_response.json()["name"]
        access_token = token_response.json()['access_token']
        email = facebook_response.json()["email"]

        return add_user_into_db(email, name, username, social_id, access_token, SocialAuth.FACEBOOK)
    else:
        raise BadRequestException(message=f'Something went wrong with {SocialAuth.FACEBOOK.value}. Try again.')


def add_user_into_db(email: str, name: str, username: str, social_id: str, access_token: str, social_type: SocialAuth):
    """
    Adds user into database
    """
    user = User.first(and_(User.social_id == social_id, User.social_type == social_type.value))
    if not user:
        # Not an existing user so get info, register and login
        user = User.first(User.email == email)
        code = 200
        with session_scope(db.session) as session:
            if user:
                user.social_access_token = access_token
                user.social_id = social_id
                user.social_type = social_type.value
            else:
                # Create the user and insert it into the database
                user = User(email=email,
                            name=name,
                            username=username,
                            social_id=social_id,
                            social_type=social_type,
                            social_access_token=access_token)
                session.add(user)
                code = 201
        # generate auth token
        auth_token = user.encode_auth_token()
        return make_response(jsonify(message=f'registered with {social_type.value} and logged in',
                                     auth_token=auth_token.decode()), code)
    else:
        auth_token = user.encode_auth_token()
        with session_scope(db.session):
            user.social_access_token = access_token
        return make_response(jsonify(message=f'logged in with {social_type.value}',
                                     auth_token=auth_token.decode()))


# TODO Review
@auth_social_blueprint.route('/auth/social/set_standalone_user', methods=['PUT'])
@accept('application/json')
@authenticate
def set_standalone_user(user_id: int):
    """
    Changes user password when logged in
    """
    post_data = request.get_json()
    if not post_data:
        raise InvalidPayloadException()
    username = post_data.get('username')
    pw_old = post_data.get('old_password')
    pw_new = post_data.get('new_password')
    if not username or not pw_old or not pw_new:
        raise InvalidPayloadException()

    # fetch the user data
    user = User.get(user_id)
    if not user.social_type:
        raise NotFoundException(message='Must be a social authenticated user login. Please try again.')

    # fetch the user data
    user = User.get(user_id)
    if not bcrypt.check_password_hash(user.password, pw_old):
        raise NotFoundException(message='Incorrect old password. Please try again.')

    if not User.first(User.username == username):
        with session_scope(db.session):
            user.username = username
            user.password = bcrypt.generate_password_hash(pw_new, current_app.config.get('BCRYPT_LOG_ROUNDS')).decode()
        return jsonify(message='Successfully changed password.')
    else:
        raise InvalidPayloadException(message='Sorry. That username already exists, choose another username')
