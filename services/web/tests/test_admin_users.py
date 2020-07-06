import json
from datetime import datetime, timedelta
from mimesis import Person
from flask import current_app

from project.models.user import User
from project.api.common.utils.constants import Constants
from project.models.user import UserRole
from tests.base import BaseTestCase
from tests.utils import add_user, add_user_password


class TestUsersBlueprint(BaseTestCase):
    """
    Test users api endpoints
    Methods include:
    CRUD calls for users
    """
    # Generate fake data with mimesis
    data_generator = Person('en')
    version = 'v1'
    url = f'/{version}/users/'
    """
    Test GET
    """

    def test_users_get(self):
        """Ensure get single user behaves correctly."""
        user = add_user()
        admin, password = add_user_password(role=UserRole.ADMIN)
        with self.client:
            resp_login = self.client.post(
                f'/{self.version}/auth/login',
                data=json.dumps(dict(
                    email=admin.email,
                    password=password
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json')]
            )
            response = self.client.get(f'{self.url}{user.id}',
                                       headers=[('Accept', 'application/json'),
                                                (Constants.HttpHeaders.AUTHORIZATION,
                                                 'Bearer ' + json.loads(resp_login.data.decode())['auth_token'])])
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertTrue('created_at' in data)
            self.assertEqual(user.email, data['email'])
            self.assertEqual(user.username, data['username'])

    def test_users_get_no_id(self):
        """Ensure error is thrown if an id is not provided."""
        admin, password = add_user_password(role=UserRole.ADMIN)
        with self.client:
            resp_login = self.client.post(
                f'/{self.version}/auth/login',
                data=json.dumps(dict(
                    email=admin.email,
                    password=password
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json')]
            )
            response = self.client.get(f'{self.url}blah', headers=[('Accept', 'application/json'), (
                Constants.HttpHeaders.AUTHORIZATION,
                'Bearer ' + json.loads(resp_login.data.decode())['auth_token'])])
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertEqual('Not Found', data['name'])

    def test_users_get_incorrect_id(self):
        """Ensure error is thrown if the id does not exist."""
        admin, password = add_user_password(role=UserRole.ADMIN)
        with self.client:
            resp_login = self.client.post(
                f'/{self.version}/auth/login',
                data=json.dumps(dict(
                    email=admin.email,
                    password=password
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json')]
            )
            response = self.client.get(f'{self.url}999', headers=[('Accept', 'application/json'), (
                Constants.HttpHeaders.AUTHORIZATION,
                'Bearer ' + json.loads(resp_login.data.decode())['auth_token'])])
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertEqual('user does not exist', data['message'])

    """
    Test POST
    """

    def test_users_post(self):
        """Ensure a new user can be added to the database."""
        admin, password = add_user_password(role=UserRole.ADMIN)
        with self.client:
            resp_login = self.client.post(
                f'/{self.version}/auth/login',
                data=json.dumps(dict(
                    email=admin.email,
                    password=password
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json')]
            )

            response = self.client.post(
                f'{self.url}',
                data=json.dumps(dict(
                    email=self.data_generator.email(),
                    username=self.data_generator.username(),
                    name=self.data_generator.full_name(),
                    password=self.data_generator.password()
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json'), (
                    Constants.HttpHeaders.AUTHORIZATION,
                    'Bearer ' + json.loads(resp_login.data.decode())['auth_token'])]
            )
            self.assertEqual(response.status_code, 201)
            data = json.loads(response.data.decode())
            self.assertEqual('user was added', data['message'])

    def test_users_post_invalid_json(self):
        """Ensure error is thrown if the JSON object is empty."""
        admin, password = add_user_password(role=UserRole.ADMIN)
        with self.client:
            resp_login = self.client.post(
                f'/{self.version}/auth/login',
                data=json.dumps(dict(
                    email=admin.email,
                    password=password
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json')]
            )
            response = self.client.post(
                f'{self.url}',
                data=json.dumps(dict()),
                content_type='application/json',
                headers=[('Accept', 'application/json'), (
                    Constants.HttpHeaders.AUTHORIZATION,
                    'Bearer ' + json.loads(resp_login.data.decode())['auth_token'])]
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertEqual('Invalid Payload', data['message'])

    def test_users_post_no_email(self):
        """Ensure error is thrown if the JSON does not have an email key."""
        admin, password = add_user_password(role=UserRole.ADMIN)
        with self.client:
            resp_login = self.client.post(
                f'/{self.version}/auth/login',
                data=json.dumps(dict(
                    email=admin.email,
                    password=password
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json')]
            )
            response = self.client.post(
                f'{self.url}',
                data=json.dumps(dict(
                    username=self.data_generator.username(),
                    name=self.data_generator.full_name(),
                    password=self.data_generator.password()
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json'), (
                    Constants.HttpHeaders.AUTHORIZATION,
                    'Bearer ' + json.loads(resp_login.data.decode())['auth_token'])]
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertEqual(data['message'], 'Validation Error')
            self.assertEqual(data['errors'][0]['field'], 'email')

    def test_users_post_no_username(self):
        """Ensure error is thrown if the JSON does not have a username key."""
        admin, password = add_user_password(role=UserRole.ADMIN)
        with self.client:
            resp_login = self.client.post(
                f'/{self.version}/auth/login',
                data=json.dumps(dict(
                    email=admin.email,
                    password=password
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json')]
            )
            response = self.client.post(
                f'{self.url}',
                data=json.dumps(dict(
                    email=self.data_generator.email(),
                    name=self.data_generator.full_name(),
                    password=self.data_generator.password()
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json'), (Constants.HttpHeaders.AUTHORIZATION,
                                                          'Bearer ' + json.loads(resp_login.data.decode())[
                                                              'auth_token'])]
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertEqual(data['message'], 'Validation Error')
            self.assertEqual(data['errors'][0]['field'], 'username')

    def test_users_post_no_name(self):
        """Ensure error is thrown if the JSON does not have a name key."""
        admin, password = add_user_password(role=UserRole.ADMIN)
        with self.client:
            resp_login = self.client.post(
                f'/{self.version}/auth/login',
                data=json.dumps(dict(
                    email=admin.email,
                    password=password
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json')]
            )
            response = self.client.post(
                f'{self.url}',
                data=json.dumps(dict(
                    email=self.data_generator.email(),
                    username=self.data_generator.username(),
                    password=self.data_generator.password()
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json'), (Constants.HttpHeaders.AUTHORIZATION,
                                                          'Bearer ' + json.loads(resp_login.data.decode())[
                                                              'auth_token'])]
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertEqual(data['message'], 'Validation Error')
            self.assertEqual(data['errors'][0]['field'], 'name')

    def test_users_post_duplicate_email(self):
        """Ensure error is thrown if the email already exists."""
        admin, password = add_user_password(role=UserRole.ADMIN)
        email = self.data_generator.email()
        with self.client:
            resp_login = self.client.post(
                f'/{self.version}/auth/login',
                data=json.dumps(dict(
                    email=admin.email,
                    password=password
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json')]
            )
            auth_token = json.loads(resp_login.data.decode())['auth_token']
            self.client.post(
                f'{self.url}',
                data=json.dumps(dict(
                    email=email,
                    username=self.data_generator.username(),
                    name=self.data_generator.full_name(),
                    password=self.data_generator.password()
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json'), (
                    Constants.HttpHeaders.AUTHORIZATION, 'Bearer ' + auth_token)]
            )
            response = self.client.post(
                f'{self.url}',
                data=json.dumps(dict(
                    email=email,
                    username=self.data_generator.username(),
                    name=self.data_generator.full_name(),
                    password=self.data_generator.password()
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json'), (
                    Constants.HttpHeaders.AUTHORIZATION, 'Bearer ' + auth_token)]
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertEqual(data['message'], 'Validation Error')
            self.assertEqual(data['errors'][0]['field'], 'email')
            self.assertEqual(data['errors'][0]['message'], 'email already exists')

    def test_users_post_duplicate_username(self):
        """Ensure error is thrown if the username already exists."""
        admin, password = add_user_password(role=UserRole.ADMIN)
        username = self.data_generator.username()
        with self.client:
            resp_login = self.client.post(
                f'/{self.version}/auth/login',
                data=json.dumps(dict(
                    email=admin.email,
                    password=password
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json')]
            )
            auth_token = json.loads(resp_login.data.decode())['auth_token']
            self.client.post(
                f'{self.url}',
                data=json.dumps(dict(
                    email=self.data_generator.email(),
                    username=username,
                    name=self.data_generator.full_name(),
                    password=self.data_generator.password()
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json'), (Constants.HttpHeaders.AUTHORIZATION,
                                                          'Bearer ' + auth_token)]
            )
            response = self.client.post(
                f'{self.url}',
                data=json.dumps(dict(
                    email=self.data_generator.email(),
                    username=username,
                    name=self.data_generator.full_name(),
                    password=self.data_generator.password()
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json'), (Constants.HttpHeaders.AUTHORIZATION,
                                                          'Bearer ' + json.loads(resp_login.data.decode())[
                                                              'auth_token'])]
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertEqual(data['message'], 'Validation Error')
            self.assertEqual(data['errors'][0]['field'], 'username')
            self.assertEqual(data['errors'][0]['message'], 'username already exists')

    def test_users_post_duplicate_name(self):
        """Ensure no error is thrown if the username and email are unique."""
        admin, password = add_user_password(role=UserRole.ADMIN)
        name = self.data_generator.full_name()
        user_password = self.data_generator.password()
        with self.client:
            resp_login = self.client.post(
                f'/{self.version}/auth/login',
                data=json.dumps(dict(
                    email=admin.email,
                    password=password
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json')]
            )
            auth_token = json.loads(resp_login.data.decode())['auth_token']
            self.client.post(
                f'{self.url}',
                data=json.dumps(dict(
                    email=self.data_generator.email(),
                    username=self.data_generator.username(),
                    name=name,
                    password=user_password
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json'), (Constants.HttpHeaders.AUTHORIZATION,
                                                          'Bearer ' + auth_token)]
            )
            response = self.client.post(
                f'{self.url}',
                data=json.dumps(dict(
                    email=self.data_generator.email(),
                    username=self.data_generator.username(),
                    name=name,
                    password=user_password
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json'), (Constants.HttpHeaders.AUTHORIZATION,
                                                          'Bearer ' + auth_token)]
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 201)
            self.assertEqual('user was added', data['message'])

    def test_users_post_valid_role(self):
        """Ensure a new user can with given role can be added to the database."""
        admin, password = add_user_password(role=UserRole.ADMIN)
        email = self.data_generator.email()
        with self.client:
            resp_login = self.client.post(
                f'/{self.version}/auth/login',
                data=json.dumps(dict(
                    email=admin.email,
                    password=password
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json')]
            )
            response = self.client.post(
                f'{self.url}',
                data=json.dumps(dict(
                    email=email,
                    username=self.data_generator.username(),
                    name=self.data_generator.full_name(),
                    password=self.data_generator.password(),
                    role=UserRole.ADMIN
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json'), (
                    Constants.HttpHeaders.AUTHORIZATION,
                    'Bearer ' + json.loads(resp_login.data.decode())['auth_token'])]
            )
            self.assertEqual(response.status_code, 201)
            data = json.loads(response.data.decode())
            self.assertEqual('user was added', data['message'])

            user = User.first(User.email == email)
            self.assertTrue(user)
            self.assertEqual(user.role, UserRole.ADMIN)

    def test_users_post_invalid_role(self):
        """Ensure adding user with invalid role shows invalid role error and doesn't add user."""
        admin, password = add_user_password(role=UserRole.ADMIN)
        email = self.data_generator.email()
        with self.client:
            resp_login = self.client.post(
                f'/{self.version}/auth/login',
                data=json.dumps(dict(
                    email=admin.email,
                    password=password
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json')]
            )
            auth_token = json.loads(resp_login.data.decode())['auth_token']
            response = self.client.post(
                f'{self.url}',
                data=json.dumps(dict(
                    email=email,
                    username=self.data_generator.username(),
                    name=self.data_generator.full_name(),
                    password=self.data_generator.password(),
                    role='blah'
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json'), (
                    Constants.HttpHeaders.AUTHORIZATION,
                    'Bearer ' + auth_token)]
            )
            self.assertEqual(response.status_code, 400)
            data = json.loads(response.data.decode())
            self.assertEqual(data['message'], 'Validation Error')
            self.assertEqual(data['errors'][0]['field'], 'role')
            self.assertFalse(User.exists(User.email == email))

            response = self.client.post(
                f'{self.url}',
                data=json.dumps(dict(
                    email=email,
                    username=self.data_generator.username(),
                    name=self.data_generator.full_name(),
                    password=self.data_generator.password(),
                    role='9999'
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json'), (
                    Constants.HttpHeaders.AUTHORIZATION,
                    'Bearer ' + auth_token)]
            )

            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertEqual(data['message'], 'Validation Error')
            self.assertEqual(data['errors'][0]['field'], 'role')
            self.assertFalse(User.exists(User.email == email))

    def test_users_post_login_after(self):
        """Ensure an added new user can login."""
        admin, password = add_user_password(role=UserRole.ADMIN)
        with self.client:
            resp_login = self.client.post(
                f'/{self.version}/auth/login',
                data=json.dumps(dict(
                    email=admin.email,
                    password=password
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json')]
            )
            user_email = self.data_generator.email()
            user_password = self.data_generator.password()
            response = self.client.post(
                f'{self.url}',
                data=json.dumps(dict(
                    email=user_email,
                    password=user_password,
                    username=self.data_generator.username(),
                    name=self.data_generator.full_name()
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json'), (
                    Constants.HttpHeaders.AUTHORIZATION,
                    'Bearer ' + json.loads(resp_login.data.decode())['auth_token'])]
            )
            self.assertEqual(response.status_code, 201)

            response = self.client.post(
                f'/{self.version}/auth/login',
                data=json.dumps(dict(
                    email=user_email,
                    password=user_password
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json')]
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['message'], 'Successfully logged in.')
            self.assertTrue(data['auth_token'])
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.status_code, 200)

    """
    Test GET [List]
    """

    def test_users_get_all(self):
        """Ensure get all users behaves correctly."""
        created = datetime.now() + timedelta(-60)
        user1 = add_user(created_at=created)
        user2 = add_user()
        created = created + timedelta(-60)
        admin, password = add_user_password(role=UserRole.ADMIN, created_at=created)
        with self.client:
            resp_login = self.client.post(
                f'/{self.version}/auth/login',
                data=json.dumps(dict(
                    email=admin.email,
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
            self.assertEqual(len(data['users']), 3)
            self.assertTrue('per_page' in data)
            self.assertTrue('page' in data)
            self.assertTrue('number_of_pages' in data)

            self.assertTrue('created_at' in data['users'][0])
            self.assertTrue('created_at' in data['users'][1])
            self.assertTrue('created_at' in data['users'][2])
            self.assertEqual(admin.email, data['users'][2]['email'])
            self.assertEqual(user1.email, data['users'][1]['email'])
            self.assertEqual(user2.email, data['users'][0]['email'])

    def test_users_get_all_page(self):
        """Ensure page param in get all users behaves correctly."""
        admin, password = add_user_password(role=UserRole.ADMIN)

        per_page = current_app.config['POSTS_PER_PAGE']
        # Add n random users
        number_of_items = per_page
        for i in range(number_of_items):
            add_user()

        with self.client:
            resp_login = self.client.post(
                f'/{self.version}/auth/login',
                data=json.dumps(dict(
                    email=admin.email,
                    password=password
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json')]
            )
            auth_token = json.loads(resp_login.data.decode())['auth_token']

            """ Test page param"""
            params = dict(page=2)
            response = self.client.get(f'{self.url}', query_string=params,
                                       headers=[('Accept', 'application/json'),
                                                (Constants.HttpHeaders.AUTHORIZATION,
                                                 'Bearer ' + auth_token)])
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(data['users']), 1)
            self.assertEqual(data['page'], 2)
            self.assertEqual(data['users'][0]['email'], admin.email)

    def test_users_get_all_per_page(self):
        """Ensure per_page param in get all users behaves correctly."""
        # Add n random users
        number_of_items = 49
        for i in range(number_of_items):
            add_user()

        posts_per_page = current_app.config['POSTS_PER_PAGE']

        admin, password = add_user_password(role=UserRole.ADMIN)

        with self.client:
            """ Test default per page"""
            resp_login = self.client.post(
                f'/{self.version}/auth/login',
                data=json.dumps(dict(
                    email=admin.email,
                    password=password
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json')]
            )
            auth_token = json.loads(resp_login.data.decode())['auth_token']
            response = self.client.get(f'{self.url}',
                                       headers=[('Accept', 'application/json'),
                                                (Constants.HttpHeaders.AUTHORIZATION,
                                                 'Bearer ' + auth_token)])
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(data['users']), posts_per_page)
            self.assertTrue('per_page' in data)
            self.assertTrue('page' in data)
            self.assertTrue('number_of_pages' in data)

            self.assertEqual(posts_per_page, data['per_page'])
            # Add 1 for admin user
            self.assertEqual((number_of_items + 1) / posts_per_page, data['number_of_pages'])

            """ Test custom per page"""
            posts_per_page = 5
            params = dict(per_page=posts_per_page)
            response = self.client.get(f'{self.url}', query_string=params,
                                       headers=[('Accept', 'application/json'),
                                                (Constants.HttpHeaders.AUTHORIZATION,
                                                 'Bearer ' + auth_token)])
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(data['users']), posts_per_page)
            self.assertTrue('per_page' in data)
            self.assertTrue('page' in data)
            self.assertTrue('number_of_pages' in data)

            self.assertEqual(posts_per_page, data['per_page'])
            self.assertEqual((number_of_items + 1) / posts_per_page, data['number_of_pages'])

    def test_users_get_all_do_not_exceed_max_page(self):
        """Ensure per_page param query exceeding max_per_page returns only max_per_page items."""
        max_per_page = current_app.config['MAX_PER_PAGE']
        # Add n random users
        number_of_items = max_per_page + 1
        for i in range(number_of_items):
            add_user()

        admin, password = add_user_password(role=UserRole.ADMIN)
        with self.client:
            resp_login = self.client.post(
                f'/{self.version}/auth/login',
                data=json.dumps(dict(
                    email=admin.email,
                    password=password
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json')]
            )
            params = dict(per_page=(max_per_page + 1))
            response = self.client.get(f'{self.url}', query_string=params,
                                       headers=[('Accept', 'application/json'),
                                                (Constants.HttpHeaders.AUTHORIZATION,
                                                 'Bearer ' + json.loads(resp_login.data.decode())[
                                                     'auth_token'])])
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(data['users']), max_per_page)
            self.assertTrue('per_page' in data)
            self.assertEqual(data['per_page'], max_per_page)

    def test_users_get_all_filter(self):
        """Ensure filter in get all users behaves correctly."""
        # Add n random users
        number_of_items = 49
        for i in range(number_of_items):
            add_user()

        admin, password = add_user_password(role=UserRole.ADMIN)

        with self.client:
            resp_login = self.client.post(
                f'/{self.version}/auth/login',
                data=json.dumps(dict(
                    email=admin.email,
                    password=password
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json')]
            )
            params = dict(filter='(id < 3)')
            response = self.client.get(f'{self.url}', query_string=params,
                                       headers=[('Accept', 'application/json'),
                                                (Constants.HttpHeaders.AUTHORIZATION,
                                                 'Bearer ' + json.loads(resp_login.data.decode())['auth_token'])])
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(data['users']), 2)
            self.assertTrue('number_of_pages' in data)
            self.assertEqual(1, data['number_of_pages'])

    def test_users_get_all_order_by(self):
        """Ensure order_by in get all users behaves correctly."""
        user_list = []
        # Add n random users
        number_of_items = 5
        for i in range(number_of_items):
            user_list.append(add_user())

        admin, password = add_user_password(role=UserRole.ADMIN)
        user_list.append(admin)
        with self.client:
            resp_login = self.client.post(
                f'/{self.version}/auth/login',
                data=json.dumps(dict(
                    email=admin.email,
                    password=password
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json')]
            )
            auth_token = json.loads(resp_login.data.decode())['auth_token']
            """ Tests ascending order"""
            params = dict(order_by='(created_at asc)')
            response = self.client.get(f'{self.url}', query_string=params,
                                       headers=[('Accept', 'application/json'),
                                                (Constants.HttpHeaders.AUTHORIZATION,
                                                 'Bearer ' + auth_token)])
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)

            for i in range(len(data['users'])):
                self.assertEqual(data['users'][i]['email'], user_list[i].email)

            """ Tests descending order"""
            params = dict(order_by='(created_at desc)')
            response = self.client.get(f'{self.url}', query_string=params,
                                       headers=[('Accept', 'application/json'),
                                                (Constants.HttpHeaders.AUTHORIZATION,
                                                 'Bearer ' + auth_token)])
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            for i in range(len(data['users'])):
                self.assertNotEqual(data['users'][i]['email'], user_list[i].email)

    """
    Test PUT
    """

    def test_users_put(self):
        """Ensure an existing user can be updated with new data."""
        admin, password = add_user_password(role=UserRole.ADMIN)
        user = add_user()
        with self.client:
            resp_login = self.client.post(
                f'/{self.version}/auth/login',
                data=json.dumps(dict(
                    email=admin.email,
                    password=password
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json')]
            )
            email = self.data_generator.email()
            username = self.data_generator.username()
            name = self.data_generator.full_name()

            response = self.client.put(
                f'{self.url}{user.id}',
                data=json.dumps(dict(
                    email=email,
                    username=username,
                    name=name,
                    role=UserRole.ADMIN.value
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json'), (
                    Constants.HttpHeaders.AUTHORIZATION,
                    'Bearer ' + json.loads(resp_login.data.decode())['auth_token'])]
            )
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data.decode())
            self.assertEqual('user was updated', data['message'])

            self.assertEqual(email, user.email)
            self.assertEqual(username, user.username)
            self.assertEqual(name, user.name)
            self.assertEqual(UserRole.ADMIN.value, user.role)

    def test_users_put_no_change(self):
        """Ensure update call works with same data without any changes."""
        admin, password = add_user_password(role=UserRole.ADMIN)
        email = self.data_generator.email()
        username = self.data_generator.username()
        name = self.data_generator.full_name()
        user = add_user(email=email, username=username, name=name)

        with self.client:
            resp_login = self.client.post(
                f'/{self.version}/auth/login',
                data=json.dumps(dict(
                    email=admin.email,
                    password=password
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json')]
            )

            response = self.client.put(
                f'{self.url}{user.id}',
                data=json.dumps(dict(
                    email=email,
                    username=username,
                    name=name,
                    role=UserRole.ADMIN.value
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json'), (
                    Constants.HttpHeaders.AUTHORIZATION,
                    'Bearer ' + json.loads(resp_login.data.decode())['auth_token'])]
            )
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data.decode())
            self.assertEqual('user was updated', data['message'])

            self.assertEqual(email, user.email)
            self.assertEqual(username, user.username)
            self.assertEqual(name, user.name)
            self.assertEqual(UserRole.ADMIN.value, user.role)

    def test_users_put_invalid_json(self):
        """Ensure error is thrown if the JSON object is empty."""
        user = add_user()
        admin, password = add_user_password(role=UserRole.ADMIN)
        with self.client:
            resp_login = self.client.post(
                f'/{self.version}/auth/login',
                data=json.dumps(dict(
                    email=admin.email,
                    password=password
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json')]
            )
            response = self.client.put(
                f'{self.url}{user.id}',
                data=json.dumps(dict()),
                content_type='application/json',
                headers=[('Accept', 'application/json'), (
                    Constants.HttpHeaders.AUTHORIZATION,
                    'Bearer ' + json.loads(resp_login.data.decode())['auth_token'])]
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertEqual('Invalid Payload', data['message'])

    def test_users_put_no_email(self):
        """Ensure no error is thrown if the JSON does not have an email key."""
        user = add_user()
        admin, password = add_user_password(role=UserRole.ADMIN)
        username = self.data_generator.username()
        name = self.data_generator.full_name()
        with self.client:
            resp_login = self.client.post(
                f'/{self.version}/auth/login',
                data=json.dumps(dict(
                    email=admin.email,
                    password=password
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json')]
            )
            response = self.client.put(
                f'{self.url}{user.id}',
                data=json.dumps(dict(
                    username=username,
                    name=name,
                    password=self.data_generator.password()
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json'), (
                    Constants.HttpHeaders.AUTHORIZATION,
                    'Bearer ' + json.loads(resp_login.data.decode())['auth_token'])]
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual('user was updated', data['message'])
            self.assertEqual(user.username, username)
            self.assertEqual(user.name, name)

    def test_users_put_no_username(self):
        """Ensure no error is thrown if the JSON does not have a username key."""
        user = add_user()
        admin, password = add_user_password(role=UserRole.ADMIN)
        email = self.data_generator.email()
        name = self.data_generator.full_name()
        with self.client:
            resp_login = self.client.post(
                f'/{self.version}/auth/login',
                data=json.dumps(dict(
                    email=admin.email,
                    password=password
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json')]
            )
            response = self.client.put(
                f'{self.url}{user.id}',
                data=json.dumps(dict(
                    email=email,
                    name=name,
                    password=self.data_generator.password()
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json'), (Constants.HttpHeaders.AUTHORIZATION,
                                                          'Bearer ' + json.loads(resp_login.data.decode())[
                                                              'auth_token'])]
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual('user was updated', data['message'])
            self.assertEqual(user.email, email)
            self.assertEqual(user.name, name)

    def test_users_put_no_name(self):
        """Ensure no error is thrown if the JSON does not have a name key."""
        user = add_user()
        admin, password = add_user_password(role=UserRole.ADMIN)
        email = self.data_generator.email()
        username = self.data_generator.username()
        with self.client:
            resp_login = self.client.post(
                f'/{self.version}/auth/login',
                data=json.dumps(dict(
                    email=admin.email,
                    password=password
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json')]
            )
            response = self.client.put(
                f'{self.url}{user.id}',
                data=json.dumps(dict(
                    email=email,
                    username=username,
                    password=self.data_generator.password()
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json'), (Constants.HttpHeaders.AUTHORIZATION,
                                                          'Bearer ' + json.loads(resp_login.data.decode())[
                                                              'auth_token'])]
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual('user was updated', data['message'])
            self.assertEqual(user.username, username)
            self.assertEqual(user.email, email)

    def test_users_put_duplicate_email(self):
        """Ensure error is thrown if the email already exists."""
        admin, password = add_user_password(role=UserRole.ADMIN)
        email = self.data_generator.email()
        username = self.data_generator.username()
        name = self.data_generator.full_name()
        add_user(email=email)
        user = add_user()
        with self.client:
            resp_login = self.client.post(
                f'/{self.version}/auth/login',
                data=json.dumps(dict(
                    email=admin.email,
                    password=password
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json')]
            )
            auth_token = json.loads(resp_login.data.decode())['auth_token']
            response = self.client.put(
                f'{self.url}{user.id}',
                data=json.dumps(dict(
                    email=email,
                    username=username,
                    name=name,
                    password=self.data_generator.password()
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json'), (
                    Constants.HttpHeaders.AUTHORIZATION, 'Bearer ' + auth_token)]
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertEqual(data['message'], 'Validation Error')
            self.assertEqual(data['errors'][0]['field'], 'email')
            self.assertEqual(data['errors'][0]['message'], 'email already exists')
            self.assertNotEqual(user.username, username)
            self.assertNotEqual(user.email, email)
            self.assertNotEqual(user.name, name)

    def test_users_put_duplicate_username(self):
        """Ensure error is thrown if the username already exists."""
        admin, password = add_user_password(role=UserRole.ADMIN)
        email = self.data_generator.email()
        username = self.data_generator.username()
        name = self.data_generator.full_name()
        add_user(username=username)
        user = add_user()
        with self.client:
            resp_login = self.client.post(
                f'/{self.version}/auth/login',
                data=json.dumps(dict(
                    email=admin.email,
                    password=password
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json')]
            )
            auth_token = json.loads(resp_login.data.decode())['auth_token']
            response = self.client.put(
                f'{self.url}{user.id}',
                data=json.dumps(dict(
                    email=email,
                    username=username,
                    name=name,
                    password=self.data_generator.password()
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json'), (
                    Constants.HttpHeaders.AUTHORIZATION, 'Bearer ' + auth_token)]
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertEqual(data['message'], 'Validation Error')
            self.assertEqual(data['errors'][0]['field'], 'username')
            self.assertEqual(data['errors'][0]['message'], 'username already exists')
            self.assertNotEqual(user.username, username)
            self.assertNotEqual(user.email, email)
            self.assertNotEqual(user.name, name)

    def test_users_put_duplicate_name(self):
        """Ensure no error is thrown if the username and email are unique."""
        admin, password = add_user_password(role=UserRole.ADMIN)
        name = self.data_generator.full_name()
        user_password = self.data_generator.password()
        add_user(name=name, password=user_password)
        user = add_user()
        with self.client:
            resp_login = self.client.post(
                f'/{self.version}/auth/login',
                data=json.dumps(dict(
                    email=admin.email,
                    password=password
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json')]
            )
            auth_token = json.loads(resp_login.data.decode())['auth_token']
            response = self.client.put(
                f'{self.url}{user.id}',
                data=json.dumps(dict(
                    email=user.email,
                    username=user.username,
                    name=name,
                    password=user_password
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json'), (
                    Constants.HttpHeaders.AUTHORIZATION, 'Bearer ' + auth_token)]
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual('user was updated', data['message'])

    def test_users_put_valid_role(self):
        """Ensure role can be updated for user."""
        admin, password = add_user_password(role=UserRole.ADMIN)
        user = add_user()
        with self.client:
            resp_login = self.client.post(
                f'/{self.version}/auth/login',
                data=json.dumps(dict(
                    email=admin.email,
                    password=password
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json')]
            )
            response = self.client.put(
                f'{self.url}{user.id}',
                data=json.dumps(dict(
                    role=UserRole.ADMIN
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json'), (
                    Constants.HttpHeaders.AUTHORIZATION,
                    'Bearer ' + json.loads(resp_login.data.decode())['auth_token'])]
            )
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data.decode())
            self.assertEqual('user was updated', data['message'])
            self.assertEqual(user.role, UserRole.ADMIN)

    def test_users_put_invalid_role(self):
        """Ensure updating user with invalid role shows invalid role error and doesn't update user."""
        admin, password = add_user_password(role=UserRole.ADMIN)
        user = add_user()
        email = self.data_generator.email()
        username = self.data_generator.username()
        name = self.data_generator.full_name()

        with self.client:
            resp_login = self.client.post(
                f'/{self.version}/auth/login',
                data=json.dumps(dict(
                    email=admin.email,
                    password=password
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json')]
            )
            auth_token = json.loads(resp_login.data.decode())['auth_token']
            response = self.client.put(
                f'{self.url}{user.id}',
                data=json.dumps(dict(
                    username=username,
                    email=email,
                    name=name,
                    role='blah'
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json'), (
                    Constants.HttpHeaders.AUTHORIZATION,
                    'Bearer ' + auth_token)]
            )
            self.assertEqual(response.status_code, 400)
            data = json.loads(response.data.decode())
            self.assertEqual(data['message'], 'Validation Error')
            self.assertEqual(data['errors'][0]['field'], 'role')
            self.assertEqual(user.role, UserRole.USER.value)

            response = self.client.put(
                f'{self.url}{user.id}',
                data=json.dumps(dict(
                    username=username,
                    email=email,
                    name=name,
                    role='9999'
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json'), (
                    Constants.HttpHeaders.AUTHORIZATION,
                    'Bearer ' + auth_token)]
            )
            self.assertEqual(response.status_code, 400)
            data = json.loads(response.data.decode())
            self.assertEqual(data['message'], 'Validation Error')
            self.assertEqual(data['errors'][0]['field'], 'role')
            self.assertEqual(user.role, UserRole.USER.value)
            self.assertNotEqual(user.username, username)
            self.assertNotEqual(user.name, name)
            self.assertNotEqual(user.email, email)

    def test_users_put_login_after(self):
        """Ensure an updated new user can login."""
        admin, password = add_user_password(role=UserRole.ADMIN)
        with self.client:
            resp_login = self.client.post(
                f'/{self.version}/auth/login',
                data=json.dumps(dict(
                    email=admin.email,
                    password=password
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json')]
            )
            user_email = self.data_generator.email()
            user_password = self.data_generator.password()
            user = add_user()
            response = self.client.put(
                f'{self.url}{user.id}',
                data=json.dumps(dict(
                    email=user_email,
                    password=user_password,
                    username=self.data_generator.username(),
                    name=self.data_generator.full_name()
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json'), (
                    Constants.HttpHeaders.AUTHORIZATION,
                    'Bearer ' + json.loads(resp_login.data.decode())['auth_token'])]
            )
            self.assertEqual(response.status_code, 200)

            response = self.client.post(
                f'/{self.version}/auth/login',
                data=json.dumps(dict(
                    email=user_email,
                    password=user_password
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json')]
            )
            data = json.loads(response.data.decode())
            self.assertEqual(data['message'], 'Successfully logged in.')
            self.assertTrue(data['auth_token'])
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.status_code, 200)

    """
    Test DELETE
    """

    def test_users_delete(self):
        """Ensure delete single user behaves correctly."""
        admin, password = add_user_password(role=UserRole.ADMIN)
        user = add_user()
        with self.client:
            resp_login = self.client.post(
                f'/{self.version}/auth/login',
                data=json.dumps(dict(
                    email=admin.email,
                    password=password
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json')]
            )
            response = self.client.delete(
                f'{self.url}{user.id}',
                headers=[('Accept', 'application/json'),
                         (Constants.HttpHeaders.AUTHORIZATION,
                          'Bearer ' + json.loads(resp_login.data.decode())['auth_token'])])
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual('user was deleted', data['message'])

            self.assertFalse(User.exists(User.id == user.id))

            response = self.client.get(
                f'{self.url}{user.id}',
                headers=[('Accept', 'application/json'), (
                    Constants.HttpHeaders.AUTHORIZATION,
                    'Bearer ' + json.loads(resp_login.data.decode())['auth_token'])])

            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertEqual('user does not exist', data['message'])

    def test_users_delete_incorrect_id(self):
        """Ensure error is thrown if the id to be deleted does not exist."""
        admin, password = add_user_password(role=UserRole.ADMIN)
        with self.client:
            resp_login = self.client.post(
                f'/{self.version}/auth/login',
                data=json.dumps(dict(
                    email=admin.email,
                    password=password
                )),
                content_type='application/json',
                headers=[('Accept', 'application/json')]
            )
            response = self.client.delete(
                f'{self.url}999',
                headers=[('Accept', 'application/json'),
                         (Constants.HttpHeaders.AUTHORIZATION,
                          'Bearer ' + json.loads(resp_login.data.decode())['auth_token'])])
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertEqual('user does not exist', data['message'])
