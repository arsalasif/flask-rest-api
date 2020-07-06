from flask import current_app
from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from sqlalchemy import and_

from .....models.user import User, UserRole
from ..... import bcrypt


class UsersPost(BaseModel):
    email: EmailStr
    username: str
    password: str
    name: str
    role: UserRole = UserRole.USER

    @validator('email')
    def validate_email(cls, email):
        if User.exists(User.email == email):
            raise ValueError('email already exists')
        return email

    @validator('username')
    def validate_username(cls, username):
        if User.exists(User.username == username):
            raise ValueError('username already exists')
        return username


class UsersPut(BaseModel):
    model: User
    email: Optional[EmailStr]
    username: Optional[str]
    password: Optional[str]
    name: Optional[str]
    role: Optional[UserRole]
    active: Optional[bool]

    @validator('email')
    def validate_email(cls, email, values):
        if email and User.exists(and_(User.email == email, User.id != values['model'].id)):
            raise ValueError('email already exists')
        return email

    @validator('username')
    def validate_username(cls, username, values):
        if username and User.exists(and_(User.username == username, User.id != values['model'].id)):
            raise ValueError('username already exists')
        return username

    @validator('password')
    def generate_password_hash(cls, password):
        if password:
            return bcrypt.generate_password_hash(password,
                                                 current_app.config.get('BCRYPT_LOG_ROUNDS')).decode()
        return password

    class Config:
        arbitrary_types_allowed = True
