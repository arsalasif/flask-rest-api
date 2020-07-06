import json
from mimesis import Person, Cryptographic

from project.api.v1.auth.social import add_user_into_db
from project.models.user import SocialAuth
from tests.base import BaseTestCase


class TestAuthSocialBlueprint(BaseTestCase):
    """
    Test social authentication api api/v1/auth_social.py endpoints
    Methods include:
    /auth/social/set_standalone_user
    add_user_into_db method from auth_social class
    """
    # Generate fake data with mimesis
    data_generator = Person('en')

    """
    Test social_auth registration and login
    """

    def test_auth_social_register(self):
        """Ensure user can register with social authentication"""
        response = add_user_into_db(email=self.data_generator.email(),
                                    name=self.data_generator.full_name(),
                                    username=self.data_generator.username(),
                                    social_id=self.data_generator.identifier(),
                                    social_type=SocialAuth.FACEBOOK,
                                    access_token=Cryptographic.token_urlsafe())

        data = json.loads(response.data.decode())
        self.assertEqual(data['message'], f'registered with {SocialAuth.FACEBOOK.value} and logged in')
        self.assertTrue(data['auth_token'])
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.status_code, 201)

    def test_auth_social_login(self):
        """Ensure registered social user can login"""
        email = self.data_generator.email()
        name = self.data_generator.full_name()
        username = self.data_generator.username()
        social_id = self.data_generator.identifier()
        response = add_user_into_db(email=email,
                                    name=name,
                                    username=username,
                                    social_id=social_id,
                                    social_type=SocialAuth.FACEBOOK,
                                    access_token=Cryptographic.token_urlsafe())

        data = json.loads(response.data.decode())
        self.assertEqual(data['message'],
                         f'registered with {SocialAuth.FACEBOOK.value} and logged in')
        self.assertTrue(data['auth_token'])
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.status_code, 201)

        response = add_user_into_db(email=email,
                                    name=name,
                                    username=username,
                                    social_id=social_id,
                                    social_type=SocialAuth.FACEBOOK,
                                    access_token=Cryptographic.token_urlsafe())

        data = json.loads(response.data.decode())
        self.assertEqual(data['message'],
                         f'logged in with {SocialAuth.FACEBOOK.value}')
        self.assertTrue(data['auth_token'])
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.status_code, 200)
