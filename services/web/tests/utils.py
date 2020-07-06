from __future__ import annotations
from datetime import datetime
from mimesis import Person, Cryptographic, Text

from project import db, app
from project.models.user import User, UserRole, SocialAuth
from project.models.group import Group
from project.models.user_group_association import UserGroupAssociation
from project import bcrypt

data_generator = Person('en')
data_generator_text = Text()


def add_user(role: UserRole = UserRole.USER,
             email: str = None,
             username: str = None,
             password: str = None,
             created_at: datetime = None,
             name: str = None) -> User:
    """
    Generates a fake user to add in DB
    """
    if email is None:
        email = data_generator.email()
    if username is None:
        username = data_generator.email()
    if password is None:
        password = data_generator.email()
    if created_at is None:
        created_at = datetime.now()
    if name is None:
        name = data_generator.full_name()

    user = User(email=email,
                username=username,
                password=password,
                name=name,
                created_at=created_at,
                role=role)
    db.session.add(user)
    db.session.commit()
    return user


def add_user_password(role: UserRole = UserRole.USER,
                      email: str = None,
                      username: str = None,
                      password: str = None,
                      created_at: datetime = None,
                      name: str = None) -> tuple(User, str):
    """
    Generates a fake user to add in DB and return User, password tuple
    """
    if email is None:
        email = data_generator.email()
    if username is None:
        username = data_generator.email()
    if password is None:
        password = data_generator.email()
    if created_at is None:
        created_at = datetime.now()
    if name is None:
        name = data_generator.full_name()

    user = User(email=email,
                username=username,
                password=password,
                name=name,
                created_at=created_at,
                role=role)
    db.session.add(user)
    db.session.commit()
    return user, password


def add_social_user(role: UserRole = UserRole.USER,
                    email: str = None,
                    username: str = None,
                    password: str = None) -> User:
    """
    Generates a fake social user to add in DB
    """
    if email is None:
        email = data_generator.email()
    if username is None:
        username = data_generator.email()
    if password is None:
        password = data_generator.email()

    user = User(email=email,
                username=username,
                password=password,
                name=data_generator.full_name(),
                created_at=datetime.now(),
                role=role,
                social_type=SocialAuth.FACEBOOK.value,
                social_id=data_generator.identifier(),
                social_access_token=Cryptographic.token_urlsafe())
    db.session.add(user)
    db.session.commit()
    return user

def add_group(name: str) -> Group:
    """
    Add a new group in database
    """
    group = Group(name=name)
    db.session.add(group)
    db.session.commit()
    return group


def add_user_group_association(user: User, group: Group) -> UserGroupAssociation:
    """
    Add a new user-group association
    """
    user_group_association = UserGroupAssociation(user=user, group=group)
    db.session.add(user_group_association)
    db.session.commit()
    return user_group_association


def set_user_token_hash(user: User, token: str) -> User:
    """
    Set token hash for user
    """
    user.token_hash = bcrypt.generate_password_hash(token, app.config.get('BCRYPT_LOG_ROUNDS')).decode()
    db.session.commit()
    return user


def set_user_email_token_hash(user: User, token: str) -> User:
    """
    Set email token hash for user
    """
    user.email_token_hash = bcrypt.generate_password_hash(token, app.config.get('BCRYPT_LOG_ROUNDS')).decode()
    db.session.commit()
    return user
