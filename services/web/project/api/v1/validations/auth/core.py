from pydantic import BaseModel, EmailStr, validator
from .....models.user import User
from ..... import bcrypt


class UserRegister(BaseModel):
    email: EmailStr
    username: str
    password: str
    name: str
    active = False

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


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class PasswordChange(BaseModel):
    user: User
    current_password: str
    new_password: str

    @validator('current_password')
    def validate_current_password(cls, current_password, values):
        if not bcrypt.check_password_hash(values['user'].password, current_password):
            raise ValueError('Invalid current password. Please try again.')
        return current_password

    class Config:
        arbitrary_types_allowed = True


class PasswordReset(BaseModel):
    token: str
    password: str


class PasswordRecovery(BaseModel):
    email: EmailStr
