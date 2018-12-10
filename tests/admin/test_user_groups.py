from .. import util
import duo_client.admin
from .base import TestAdmin


class TestUserGroups(TestAdmin):
    def test_get_user_groups_iterator(self):
        """ Test to get groups iterator by user id.
        """
        generator = self.client_list.get_user_groups_iterator(
            'DU012345678901234567')
        response = next(generator)
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'GET')
        self.assertEqual(uri, '/admin/v1/users/DU012345678901234567/groups')
        self.assertEqual(util.params_to_dict(args),
                         {
                            'account_id':[self.client.account_id],
                            'limit': ['100'],
                            'offset': ['0'],
                         })

    def test_get_user_groups(self):
        """ Test to get groups by user id.
        """
        response = self.client_list.get_user_groups('DU012345678901234567')[0]
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'GET')
        self.assertEqual(uri, '/admin/v1/users/DU012345678901234567/groups')
        self.assertEqual(util.params_to_dict(args),
                         {
                            'account_id':[self.client.account_id],
                            'limit': ['100'],
                            'offset': ['0'],
                         })

    def test_get_user_groups_with_offset(self):
        """ Test to get groups by user id with pagination params.
        """
        response = self.client_list.get_user_groups(
            'DU012345678901234567', offset=60)[0]
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'GET')
        self.assertEqual(uri, '/admin/v1/users/DU012345678901234567/groups')
        self.assertEqual(util.params_to_dict(args),
                         {
                             'account_id':[self.client.account_id],
                             'limit': ['100'],
                             'offset': ['0'],
                         })

    def test_get_user_groups_with_limit(self):
        """ Test to get groups by user id with pagination params.
        """
        response = self.client_list.get_user_groups(
            'DU012345678901234567', limit=30)[0]
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'GET')
        self.assertEqual(uri, '/admin/v1/users/DU012345678901234567/groups')
        self.assertEqual(util.params_to_dict(args),
                         {
                             'account_id':[self.client.account_id],
                             'limit': ['30'],
                             'offset': ['0'],
                         })

    def test_get_user_groups_with_limit_and_offset(self):
        """ Test to get groups by user id with pagination params.
        """
        response = self.client_list.get_user_groups(
            'DU012345678901234567', limit=30, offset=60)[0]
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'GET')
        self.assertEqual(uri, '/admin/v1/users/DU012345678901234567/groups')
        self.assertEqual(util.params_to_dict(args),
                         {
                             'account_id':[self.client.account_id],
                             'limit': ['30'],
                             'offset': ['60'],
                         })


if __name__ == '__main__':
    unittest.main()
