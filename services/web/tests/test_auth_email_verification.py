import json
from mimesis import Person

from project.api.common.utils.constants import Constants
from tests.base import BaseTestCase
from tests.utils import add_user, set_user_email_token_hash


class TestEmailVerificationBlueprint(BaseTestCase):
    """
    Test email verification api api/v1/email_verification.py
    """
    # Generate fake data with mimesis
    data_generator = Person('en')
    version = 'v1'
    url = '/v1/email_verification/'
    
    """
    Test /email_verification
    """

    def test_email_verification(self):
        """Ensure email verification works"""
        password = self.data_generator.password()
        user = add_user(password=password)
        with self.client:
            resp_login = self.client.post(
                f'/{self.version}/auth/login',
                data=json.dumps(dict(
                    email=user.email,
                    password=password
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json')]
            )

        with self.client:
            response = self.client.get(
                f'{self.url}',
                content_type='application/json',
                headers=[('Accept', 'application/json'),
                         (Constants.HttpHeaders.AUTHORIZATION,
                          'Bearer ' + json.loads(resp_login.data.decode())['auth_token'])]
            )
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data.decode())
            self.assertEqual(data['message'], 'sent email with verification token')

    def test_email_verification_token(self):
        """Ensure email verification with token works"""
        user = add_user()
        token = user.encode_email_token().decode()
        user = set_user_email_token_hash(user, token)

        with self.client:
            response = self.client.get(
                f'{self.url}{token}',
                content_type='application/json',
                headers=[('Accept', 'application/json')]
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(data['message'], 'email verified')
            self.assertIsNotNone(user.email_validation_date)

    def test_email_verification_resend(self):
        """Ensure email verification resend works"""
        password = self.data_generator.password()
        user = add_user(password=password)
        with self.client:
            resp_login = self.client.post(
                f'/{self.version}/auth/login',
                data=json.dumps(dict(
                    email=user.email,
                    password=password
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json')]
            )

        with self.client:
            response = self.client.get(
                f'{self.url}resend',
                content_type='application/json',
                headers=[('Accept', 'application/json'),
                         (Constants.HttpHeaders.AUTHORIZATION,
                          'Bearer ' + json.loads(resp_login.data.decode())['auth_token'])]
            )
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data.decode())
            self.assertEqual(data['message'], 'verification email resent')