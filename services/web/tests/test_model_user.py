from sqlalchemy.exc import IntegrityError
from mimesis import Person

from project import db
from project.models.user import User
from tests.base import BaseTestCase
from tests.utils import add_user


class TestUserModel(BaseTestCase):
    """
    Test User model
    """
    # Generate fake data with mimesis
    data_generator = Person('en')

    def test_model_user_add_user(self):
        """Ensure adding user model works"""
        username = self.data_generator.username()
        user = add_user(username=username)
        self.assertTrue(user.id)
        self.assertEqual(user.username, username)
        self.assertTrue(user.password)
        self.assertTrue(user.active)
        self.assertTrue(user.created_at)

    def test_model_user_add_user_duplicate_username(self):
        """Ensure adding user with duplicate username does not work"""
        user = add_user()
        duplicate_user = User(
            username=user.username,
            email=self.data_generator.email(),
            password=self.data_generator.password(),
            name=self.data_generator.full_name()
        )
        db.session.add(duplicate_user)
        self.assertRaises(IntegrityError, db.session.commit)

    def test_model_user__add_user_duplicate_email(self):
        """Ensure adding user with duplicate email does not work"""
        user = add_user()
        duplicate_user = User(
            email=user.email,
            username=self.data_generator.username(),
            password=self.data_generator.password(),
            name=self.data_generator.full_name()
        )
        db.session.add(duplicate_user)
        self.assertRaises(IntegrityError, db.session.commit)

    def test_model_user_passwords_are_random(self):
        """Ensure passwords are randomly hashed"""
        password = self.data_generator.password()
        user_one = add_user(password=password)
        user_two = add_user(password=password)
        self.assertNotEqual(user_one.password, user_two.password)

    def test_model_user_encode_auth_token(self):
        """Ensure encoding auth token works"""
        user = add_user()
        auth_token = user.encode_auth_token()
        self.assertTrue(isinstance(auth_token, bytes))

    def test_model_user_decode_auth_token(self):
        """Ensure decoding auth token works"""
        user = add_user()
        auth_token = user.encode_auth_token()
        self.assertTrue(isinstance(auth_token, bytes))
        self.assertTrue(User.decode_auth_token(auth_token), user.id)