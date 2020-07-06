from __future__ import annotations
import jwt
from enum import Enum, IntFlag
from datetime import datetime, timedelta
from flask import current_app
from sqlalchemy.ext.associationproxy import association_proxy
import json

from .base import Base
from .. import db, bcrypt
from ..api.common.utils.exceptions import UnauthorizedException, BadRequestException


class UserRole(IntFlag):
    """"
    User role
    """
    USER = 1
    ADMIN = 2


class SocialAuth(Enum):
    """
    Social authentication providers
    """
    FACEBOOK = 'Facebook'
    GITHUB = 'GitHub'


class User(Base):
    """
    User model
    """
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(128), unique=True, nullable=False)
    username = db.Column(db.String(128), unique=True, nullable=False)
    name = db.Column(db.String(128), nullable=False)
    active = db.Column(db.Boolean, default=True, nullable=False)
    role = db.Column(db.Integer, default=UserRole.USER.value, nullable=False)
    password = db.Column(db.String(255), nullable=True)
    token_hash = db.Column(db.String(255), nullable=True)
    email_token_hash = db.Column(db.String(255), nullable=True)
    email_validation_date = db.Column(db.DateTime, nullable=True)

    # Social
    social_id = db.Column(db.String(128), unique=True, nullable=True)
    social_type = db.Column(db.String(64), default=None, nullable=True)
    social_access_token = db.Column(db.String, nullable=True)

    # Foreign relationships
    associated_groups = db.relationship("UserGroupAssociation", back_populates="user")
    groups = association_proxy('associated_groups', 'group')

    def __init__(self,
                 email: str,
                 username: str,
                 password: str = None,
                 name: str = None,
                 active: bool = True,
                 email_validation_date: datetime = None,
                 role: UserRole = UserRole.USER,
                 social_id: str = None,
                 social_type: SocialAuth = None,
                 social_access_token: str = None,
                 created_at: datetime = datetime.now(),
                 updated_at: datetime = datetime.now(),
                 **kwargs):
        super().__init__(created_at, updated_at)
        self.email = email
        self.username = username
        self.name = name
        if password:
            self.password = bcrypt.generate_password_hash(password,
                                                          current_app.config.get('BCRYPT_LOG_ROUNDS')).decode()
        self.active = active
        self.role = role.value
        self.email_validation_date = email_validation_date
        if social_type:
            self.social_id = social_id
            self.social_type = social_type.value
            self.social_access_token = social_access_token

    def json(self) -> json:
        """
        Get user data in JSON format
        """
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'name': self.name,
            'active': self.active,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'role': self.role,
            'role_name': UserRole(self.role).name,
            'social_type': self.social_type,
            'email_validation_date': self.email_validation_date
        }

    def encode_auth_token(self) -> str:
        """
        Generates the auth token
        """
        payload = {
            'exp': datetime.utcnow() + timedelta(
                days=current_app.config['TOKEN_EXPIRATION_DAYS'],
                seconds=current_app.config['TOKEN_EXPIRATION_SECONDS']),
            'iat': datetime.utcnow(),
            'sub': self.id
        }
        return jwt.encode(
            payload,
            current_app.config.get('SECRET_KEY'),
            algorithm='HS256'
        )

    @staticmethod
    def decode_auth_token(auth_token: str) -> int:
        """
        Decodes the auth token - :param auth_token: - :return: integer|string
        """
        try:
            payload = jwt.decode(auth_token, current_app.config.get('SECRET_KEY'))
            return payload['sub']
        except jwt.ExpiredSignatureError:
            raise UnauthorizedException(message='Signature expired. Please log in again.')
        except jwt.InvalidTokenError:
            raise UnauthorizedException(message='Invalid token. Please log in again.')

    def encode_password_token(self) -> bytes:
        """
        Generates the auth token
        """
        payload = {
            'exp': datetime.utcnow() + timedelta(
                days=current_app.config['TOKEN_PASSWORD_EXPIRATION_DAYS'],
                seconds=current_app.config['TOKEN_PASSWORD_EXPIRATION_SECONDS']),
            'iat': datetime.utcnow(),
            'sub': self.id
        }
        return jwt.encode(
            payload,
            current_app.config.get('SECRET_KEY'),
            algorithm='HS256'
        )

    @staticmethod
    def decode_password_token(pass_token: str) -> int:
        """
        Decodes the auth token - :param auth_token: - :return: integer|string
        """
        try:
            payload = jwt.decode(pass_token, current_app.config.get('SECRET_KEY'))
            return payload['sub']
        except jwt.ExpiredSignatureError:
            raise BadRequestException(message='Password recovery token expired. Please try again.')
        except jwt.InvalidTokenError:
            raise BadRequestException(message='Invalid password recovery token. Please try again.')

    def encode_email_token(self) -> bytes:
        """
        Generates the email token
        """
        payload = {
            'exp': datetime.utcnow() + timedelta(
                days=current_app.config['TOKEN_EMAIL_EXPIRATION_DAYS'],
                seconds=current_app.config['TOKEN_EMAIL_EXPIRATION_SECONDS']),
            'iat': datetime.utcnow(),
            'sub': self.id
        }
        return jwt.encode(
            payload,
            current_app.config.get('SECRET_KEY'),
            algorithm='HS256'
        )

    @staticmethod
    def decode_email_token(email_token: str) -> int:
        """
        Decodes the email token - :param auth_token: - :return: integer|string
        """
        try:
            payload = jwt.decode(email_token, current_app.config.get('SECRET_KEY'))
            return payload['sub']
        except jwt.ExpiredSignatureError:
            raise BadRequestException(message='Email recovery token expired. Please try again.')
        except jwt.InvalidTokenError:
            raise BadRequestException(message='Invalid email verification token. Please try again.')