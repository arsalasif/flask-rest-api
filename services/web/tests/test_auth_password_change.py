import json
import time
from mimesis import Person

from project.api.common.utils.constants import Constants
from tests.base import BaseTestCase
from tests.utils import add_user, set_user_token_hash


class TestAuthPasswordChangeBlueprint(BaseTestCase):
    """
    Test authentication api api/v1/auth.py password change/recovery endpoints
    Methods include:
    /auth/password_change
    /auth/password_reset
    /auth/password_recovery
    """
    # Generate fake data with mimesis
    data_generator = Person('en')
    version = 'v1'
    """
    Test /auth/password_change
    """

    def test_auth_password_change(self):
        """Ensure password change works by changing password and logging again"""
        password = self.data_generator.password()
        user = add_user(password=password)
        new_password = self.data_generator.password()
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

            response = self.client.put(
                f'/{self.version}/auth/password_change',
                data=json.dumps(dict(
                    current_password=password,
                    new_password=new_password
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json'), (
                    Constants.HttpHeaders.AUTHORIZATION,
                    'Bearer ' + json.loads(resp_login.data.decode())['auth_token'])]
            )
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data.decode())
            self.assertEqual(data['message'], 'Successfully changed password.')

            resp_login = self.client.post(
                f'/{self.version}/auth/login',
                data=json.dumps(dict(
                    email=user.email,
                    password=new_password
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json')]
            )
            data = json.loads(resp_login.data.decode())
            self.assertEqual(data['message'], 'Successfully logged in.')
            self.assertTrue(data['auth_token'])
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.status_code, 200)

    def test_auth_password_change_incorrect_password(self):
        """Ensure password change doesn't work with incorrect password"""
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

            response = self.client.put(
                f'/{self.version}/auth/password_change',
                data=json.dumps(dict(
                    current_password=self.data_generator.password(),
                    new_password=self.data_generator.password()
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json'),
                         (Constants.HttpHeaders.AUTHORIZATION,
                          'Bearer ' + json.loads(resp_login.data.decode())['auth_token'])]
            )
            self.assertEqual(response.status_code, 400)
            data = json.loads(response.data.decode())
            self.assertEqual(data['message'], 'Validation Error')
            self.assertEqual(data['errors'][0]['field'], 'current_password')
            self.assertEqual(data['errors'][0]['message'], 'Invalid current password. Please try again.')

    """
    Test /auth/password_reset
    """

    def test_auth_password_reset(self):
        """Ensure password reset works"""
        user = add_user()
        password = user.password
        token = user.encode_password_token().decode()
        set_user_token_hash(user, token)

        new_password = self.data_generator.password()

        with self.client:
            response = self.client.put(
                f'/{self.version}/auth/password_reset',
                data=json.dumps(dict(
                    token=token,
                    password=new_password
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json')]
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['message'], 'Successfully reset password.')
            self.assertEqual(response.status_code, 200)
            #  check db password have really changed
            self.assertNotEqual(password, user.password)

    def test_auth_password_reset_token_expired(self):
        """Ensure password reset with expired token does not work"""
        user = add_user()
        token = user.encode_password_token().decode()
        user = set_user_token_hash(user, token)
        user_password_before = user.password
        time.sleep(3)

        with self.client:
            response = self.client.put(
                f'/{self.version}/auth/password_reset',
                data=json.dumps(dict(
                    token=token,
                    password=self.data_generator.password()
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json')]
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['message'], 'Password recovery token expired. Please try again.')
            self.assertEqual(response.status_code, 400)
            #  check db password has not changed
            self.assertEqual(user_password_before, user.password)

    def test_auth_password_reset_token_used(self):
        """Ensure password reset with already used token does not work"""
        user = add_user()
        token = user.encode_password_token().decode()

        user = set_user_token_hash(user, token)

        with self.client:
            response = self.client.put(
                f'/{self.version}/auth/password_reset',
                data=json.dumps(dict(
                    token=token,
                    password=self.data_generator.password()
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json')]
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['message'], 'Successfully reset password.')
            self.assertEqual(response.status_code, 200)

        user_password_before = user.password

        with self.client:
            response = self.client.put(
                f'/{self.version}/auth/password_reset',
                data=json.dumps(dict(
                    token=token,
                    password=self.data_generator.password()
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json')]
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['message'], 'Invalid password reset token. Please try again.')
            self.assertEqual(response.status_code, 400)
            #  check db password has not changed
            self.assertEqual(user_password_before, user.password)

    """
    Test /auth/password_recovery
    """

    def test_auth_password_recovery(self):
        """Ensure password recovery works"""
        user = add_user()

        with self.client:
            response = self.client.post(
                f'/{self.version}/auth/password_recovery',
                data=json.dumps(dict(
                    email=user.email
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json')]
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['message'], 'Password recovery email sent.')
            self.assertEqual(response.status_code, 200)

    def test_auth_password_recovery_user_not_registered(self):
        """Ensure password recovery doesn't work with unregistered user"""
        with self.client:
            response = self.client.post(
                f'/{self.version}/auth/password_recovery',
                data=json.dumps(dict(
                    email=self.data_generator.email()
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json')]
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertEqual('Email does not exist.', data['message'])

    def test_auth_passwords_token_hash_are_random(self):
        """Ensure password recovery token hashes are random"""
        user = add_user()

        with self.client:
            response = self.client.post(
                f'/{self.version}/auth/password_recovery',
                data=json.dumps(dict(
                    email=user.email
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json')]
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['message'], 'Password recovery email sent.')
            self.assertEqual(response.status_code, 200)

        user_2 = add_user()

        with self.client:
            response = self.client.post(
                f'/{self.version}/auth/password_recovery',
                data=json.dumps(dict(
                    email=user_2.email
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json')]
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['message'], 'Password recovery email sent.')
            self.assertEqual(response.status_code, 200)

        self.assertTrue(user.token_hash != user_2.token_hash)
        self.assertTrue(user.token_hash is not None)
        self.assertTrue(user.token_hash != "")