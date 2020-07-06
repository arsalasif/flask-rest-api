from mimesis import Person

from tests.base import BaseTestCase
from tests.utils import add_user, add_group, add_user_group_association


class TestGroupModel(BaseTestCase):
    """
    Test Group model
    """
    # Generate fake data with mimesis
    data_generator = Person('en')

    def test_model_group_add_group(self):
        """Ensure a group can be added"""
        group_name = self.data_generator.occupation()
        group = add_group(name=group_name)
        self.assertTrue(group.id)
        self.assertEqual(group.name, group_name)
        self.assertTrue(group.created_at)
        self.assertTrue(group.updated_at)
        self.assertEqual(len(group.associated_users), 0)
        self.assertEqual(len(group.users), 0)

    def test_model_group_verify_associated_users(self):
        """Ensure an added group has associated users"""
        user = add_user()
        group_name = self.data_generator.occupation()
        group = add_group(name=group_name)
        self.assertEqual(len(group.associated_users), 0)
        add_user_group_association(user=user, group=group)
        self.assertEqual(len(group.associated_users), 1)
        self.assertEqual(group.associated_users[0].user.username, user.username)
        self.assertEqual(len(group.users), 1)
        self.assertEqual(group.users[0].username, user.username)
        self.assertEqual(len(user.groups), 1)
        self.assertEqual(user.groups[0].name, group_name)