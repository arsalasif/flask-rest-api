import json
import time
from mimesis import Person

from project.api.common.utils.constants import Constants
from tests.base import BaseTestCase
from tests.utils import add_user, add_user_password


class TestAuthCore(BaseTestCase):
    """
    Test authentication api api/v1/auth.py core endpoints
    Methods include:
    /auth/register
    /auth/login
    /auth/logout
    /auth/status
    /user --> to get user info
    """
    # Generate fake data with mimesis
    data_generator = Person('en')

    """
    Test /auth/register
    """

    def test_auth_register(self):
        """Ensure normal registration works"""
        with self.client:
            response = self.client.post(
                '/v1/auth/register',
                data=json.dumps(dict(
                    username=self.data_generator.username(),
                    email=self.data_generator.email(),
                    name=self.data_generator.full_name(),
                    password=self.data_generator.password()
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json')]
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['message'], 'Successfully registered.')
            self.assertTrue(data['auth_token'])
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.status_code, 201)

    def test_auth_register_duplicate_email(self):
        """Ensure duplicate email registration is not allowed"""
        user = add_user()
        with self.client:
            response = self.client.post(
                '/v1/auth/register',
                data=json.dumps(dict(
                    username=self.data_generator.username(),
                    email=user.email,
                    password=self.data_generator.password(),
                    name=self.data_generator.full_name()
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json')]
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertEqual(data['message'], 'Validation Error')
            self.assertEqual(data['errors'][0]['field'], 'email')
            self.assertEqual(data['errors'][0]['message'], 'email already exists')

    def test_auth_register_duplicate_username(self):
        """Ensure duplicate username registration is not allowed"""
        user = add_user()
        with self.client:
            response = self.client.post(
                '/v1/auth/register',
                data=json.dumps(dict(
                    username=user.username,
                    email=self.data_generator.email(),
                    password=self.data_generator.password(),
                    name=self.data_generator.full_name()
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json')]
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertEqual(data['message'], 'Validation Error')
            self.assertEqual(data['errors'][0]['field'], 'username')
            self.assertEqual(data['errors'][0]['message'], 'username already exists')

    def test_auth_register_duplicate_allowable(self):
        """Ensure duplicate password/name is allowed"""
        user = add_user()
        with self.client:
            response = self.client.post(
                '/v1/auth/register',
                data=json.dumps(dict(
                    username=self.data_generator.username(),
                    email=self.data_generator.email(),
                    password=user.password,
                    name=user.name
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json')]
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['message'], 'Successfully registered.')
            self.assertTrue(data['auth_token'])
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.status_code, 201)

    def test_auth_register_invalid_json_no_email(self):
        """Ensure registration is not allowed without email"""
        with self.client:
            response = self.client.post(
                '/v1/auth/register',
                data=json.dumps(dict(
                    username=self.data_generator.username(),
                    password=self.data_generator.password(),
                    name=self.data_generator.full_name()
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json')]
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertEqual(data['message'], 'Validation Error')
            self.assertEqual(data['errors'][0]['field'], 'email')

    def test_auth_register_invalid_json_no_username(self):
        """Ensure registration is not allowed without username"""
        with self.client:
            response = self.client.post(
                '/v1/auth/register',
                data=json.dumps(dict(
                    email=self.data_generator.email(),
                    password=self.data_generator.password(),
                    name=self.data_generator.full_name()
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json')]
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertEqual(data['message'], 'Validation Error')
            self.assertEqual(data['errors'][0]['field'], 'username')

    def test_auth_register_invalid_json_no_name(self):
        """Ensure registration is not allowed without name"""
        with self.client:
            response = self.client.post(
                '/v1/auth/register',
                data=json.dumps(dict(
                    email=self.data_generator.email(),
                    password=self.data_generator.password(),
                    username=self.data_generator.username()
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json')]
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertEqual(data['message'], 'Validation Error')
            self.assertEqual(data['errors'][0]['field'], 'name')

    def test_auth_register_invalid_json_no_password(self):
        """Ensure registration is not allowed without password"""
        with self.client:
            response = self.client.post(
                '/v1/auth/register',
                data=json.dumps(dict(
                    email=self.data_generator.email(),
                    username=self.data_generator.username(),
                    name=self.data_generator.full_name()
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json')]
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertEqual(data['message'], 'Validation Error')
            self.assertEqual(data['errors'][0]['field'], 'password')

    def test_auth_register_empty_json(self):
        """Ensure empty json gives valid error"""
        with self.client:
            response = self.client.post(
                '/v1/auth/register',
                data=json.dumps(dict()),
                content_type='application/json',
                headers=[('Accept', 'application/json')]
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertEqual('Invalid Payload', data['message'])

    """
    Test /auth/login
    """

    def test_auth_login(self):
        """Ensure registered user can login"""
        user, password = add_user_password()
        with self.client:
            response = self.client.post(
                '/v1/auth/login',
                data=json.dumps(dict(
                    email=user.email,
                    password=password
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json')]
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['message'], 'Successfully logged in.')
            self.assertTrue(data['auth_token'])
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.status_code, 200)

    def test_auth_login_no_password(self):
        """Ensure registered user cannot login without password"""
        user = add_user()
        with self.client:
            response = self.client.post(
                '/v1/auth/login',
                data=json.dumps(dict(
                    email=user.email
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json')]
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['message'], 'Validation Error')
            self.assertEqual(data['errors'][0]['field'], 'password')
            self.assertEqual(response.status_code, 400)

    def test_auth_login_no_email(self):
        """Ensure registered user cannot login without email"""
        user, password = add_user_password()
        with self.client:
            response = self.client.post(
                '/v1/auth/login',
                data=json.dumps(dict(
                    password=password
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json')]
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['message'], 'Validation Error')
            self.assertEqual(data['errors'][0]['field'], 'email')
            self.assertEqual(response.status_code, 400)

    def test_auth_login_incorrect_password(self):
        """Ensure registered user cannot login with incorrect password"""
        user = add_user()
        with self.client:
            response = self.client.post(
                '/v1/auth/login',
                data=json.dumps(dict(
                    email=user.email,
                    password=self.data_generator.password()
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json')]
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['message'], 'Incorrect password.')
            self.assertEqual(response.status_code, 400)

    def test_auth_login_not_registered(self):
        """Ensure not registered user cannot login"""
        with self.client:
            response = self.client.post(
                '/v1/auth/login',
                data=json.dumps(dict(
                    email=self.data_generator.email(),
                    password=self.data_generator.password()
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json')]
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['message'], 'User does not exist.')
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.status_code, 404)

    """
    Test /auth/logout
    """

    def test_auth_logout(self):
        """Ensure auth logout works"""
        user, password = add_user_password()
        with self.client:
            # User login
            resp_login = self.client.post(
                '/v1/auth/login',
                data=json.dumps(dict(
                    email=user.email,
                    password=password
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json')]
            )
            # Valid token logout
            response = self.client.get(
                '/v1/auth/logout',
                headers=[('Accept', 'application/json'),
                         (Constants.HttpHeaders.AUTHORIZATION,
                          'Bearer ' + json.loads(resp_login.data.decode())['auth_token'])]
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['message'], 'Successfully logged out.')
            self.assertEqual(response.status_code, 200)

    def test_auth_logout_expired_token(self):
        """Ensure logout doesn't work with expired token"""
        user, password = add_user_password()
        with self.client:
            resp_login = self.client.post(
                '/v1/auth/login',
                data=json.dumps(dict(
                    email=user.email,
                    password=password
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json')]
            )
            # Invalid token logout
            time.sleep(4)
            response = self.client.get(
                '/v1/auth/logout',
                headers=[('Accept', 'application/json'),
                         (Constants.HttpHeaders.AUTHORIZATION,
                          'Bearer ' + json.loads(resp_login.data.decode())['auth_token'])]
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['message'], 'Signature expired. Please log in again.')
            self.assertEqual(response.status_code, 401)

    def test_auth_logout_no_token(self):
        """Ensure logout shows invalid token"""
        with self.client:
            response = self.client.get(
                '/v1/auth/logout',
                headers=[('Accept', 'application/json'), (Constants.HttpHeaders.AUTHORIZATION, 'Bearer invalid')])
            data = json.loads(response.data.decode())
            self.assertEqual(data['message'], 'Invalid token. Please log in again.')
            self.assertEqual(response.status_code, 401)

    """
    Test /auth/status
    """

    def test_auth_status(self):
        """Ensure auth status check works"""
        user, password = add_user_password()
        with self.client:
            resp_login = self.client.post(
                '/v1/auth/login',
                data=json.dumps(dict(
                    email=user.email,
                    password=password
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json')]
            )
            response = self.client.get(
                '/v1/auth/status',
                headers=[('Accept', 'application/json'), (
                    Constants.HttpHeaders.AUTHORIZATION,
                    'Bearer ' + json.loads(resp_login.data.decode())['auth_token'])]
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['email'], user.email)
            self.assertEqual(data['username'], user.username)
            self.assertEqual(data['name'], user.name)
            self.assertTrue(data['active'] is True)
            self.assertTrue(data['created_at'])
            self.assertEqual(response.status_code, 200)

    def test_auth_status_invalid(self):
        """Ensure invalid token doesn't work for status check"""
        with self.client:
            response = self.client.get(
                '/v1/auth/status',
                headers=[('Accept', 'application/json'), (Constants.HttpHeaders.AUTHORIZATION, 'Bearer invalid')]
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['message'], 'Invalid token. Please log in again.')
            self.assertEqual(response.status_code, 401)

    """
    Test /user
    """

    def test_user_info(self):
        """Ensure user info works"""
        user, password = add_user_password()
        with self.client:
            resp_login = self.client.post(
                '/v1/auth/login',
                data=json.dumps(dict(
                    email=user.email,
                    password=password
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json')]
            )
            response = self.client.get(
                '/v1/user/',
                headers=[('Accept', 'application/json'), (
                    Constants.HttpHeaders.AUTHORIZATION,
                    'Bearer ' + json.loads(resp_login.data.decode())['auth_token'])]
            )

            data = json.loads(response.data.decode())
            self.assertEqual(data['email'], user.email)
            self.assertEqual(data['username'], user.username)
            self.assertEqual(data['name'], user.name)
            self.assertEqual(data['social_type'], user.social_type)
            self.assertEqual(data['social_id'], user.social_id)
            self.assertTrue(data['active'] is True)
            self.assertTrue(data['created_at'])
            self.assertEqual(response.status_code, 200)

    def test_user_info_invalid(self):
        """Ensure invalid token doesn't work for user info"""
        with self.client:
            response = self.client.get(
                '/v1/user/',
                headers=[('Accept', 'application/json'),
                         (Constants.HttpHeaders.AUTHORIZATION, 'Bearer invalid')]
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['message'], 'Invalid token. Please log in again.')
            self.assertEqual(response.status_code, 401)