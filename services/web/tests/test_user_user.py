import json
from project.api.common.utils.constants import Constants
from tests.base import BaseTestCase
from tests.utils import add_user_password


class TestUserBlueprint(BaseTestCase):
    """
    Test users api endpoints
    Methods include:
    CRUD calls for users
    """
    version = 'v1'
    url = f'/{version}/user/'

    """
    Test GET
    """

    def test_user_get(self):
        """Ensure get single user behaves correctly."""
        user, password = add_user_password()
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
            response = self.client.get(f'{self.url}',
                                       headers=[('Accept', 'application/json'),
                                                (Constants.HttpHeaders.AUTHORIZATION,
                                                 'Bearer ' + json.loads(resp_login.data.decode())['auth_token'])])
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertTrue('created_at' in data)
            self.assertEqual(user.email, data['email'])
            self.assertEqual(user.username, data['username'])