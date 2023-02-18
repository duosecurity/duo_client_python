import warnings
from .. import util
import duo_client.admin
from .base import TestAdmin


class TestGroups(TestAdmin):
    def test_get_groups_generator(self):
        """ Test to get groups generator.
        """
        generator = self.client_list.get_groups_generator()
        response = next(generator)
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'GET')
        self.assertEqual(uri, '/admin/v1/groups')
        self.assertEqual(
            util.params_to_dict(args),
            {
                'account_id': [self.client_list.account_id],
                'limit': ['100'],
                'offset': ['0'],
            })

    def test_get_groups(self):
        """ Test to get groups without params.
        """
        response = self.client_list.get_groups()[0]
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'GET')
        self.assertEqual(uri, '/admin/v1/groups')
        self.assertEqual(
            util.params_to_dict(args),
            {
                'account_id': [self.client_list.account_id],
                'limit': ['100'],
                'offset': ['0'],
            })

    def test_get_groups_limit(self):
        """ Test to get groups with limit.
        """
        response = self.client_list.get_groups(limit='20')[0]
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'GET')
        self.assertEqual(uri, '/admin/v1/groups')
        self.assertEqual(
            util.params_to_dict(args),
            {
                'account_id': [self.client_list.account_id],
                'limit': ['20'],
                'offset': ['0'],
            })

    def test_get_groups_offset(self):
        """ Test to get groups with offset.
        """
        response = self.client_list.get_groups(offset='2')[0]
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'GET')
        self.assertEqual(uri, '/admin/v1/groups')
        self.assertEqual(
            util.params_to_dict(args),
            {
                'account_id': [self.client_list.account_id],
                'limit': ['100'],
                'offset': ['0'],
            })

    def test_get_groups_limit_offset(self):
        """ Test to get groups with limit and offset.
        """
        response = self.client_list.get_groups(limit='20', offset='2')[0]
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'GET')
        self.assertEqual(uri, '/admin/v1/groups')
        self.assertEqual(
            util.params_to_dict(args),
            {
                'account_id': [self.client_list.account_id],
                'limit': ['20'],
                'offset': ['2'],
            })

    def test_get_group_v1(self):
        """ Test for v1 API of getting specific group details
        """
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            response = self.client.get_group('ABC123', api_version=1)
            uri, args = response['uri'].split('?')

            # Assert deprecation warning generated
            self.assertEqual(len(w), 1)
            self.assertTrue(issubclass(w[0].category, DeprecationWarning))
            self.assertIn('Please migrate to the v2 API', str(w[0].message))

            self.assertEqual(response['method'], 'GET')
            self.assertEqual(uri, '/admin/v1/groups/ABC123')
            self.assertEqual(util.params_to_dict(args),
                             {'account_id': [self.client.account_id]})

    def test_get_group_v2(self):
        """ Test for v2 API of getting specific group details
        """
        response = self.client.get_group('ABC123', api_version=2)
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'GET')
        self.assertEqual(uri, '/admin/v2/groups/ABC123')
        self.assertEqual(util.params_to_dict(args),
                         {'account_id': [self.client.account_id]})

    def test_get_group_users(self):
        """ Test for getting list of users associated with a group
        """
        response = self.client_list.get_group_users('ABC123')[0]
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'GET')
        self.assertEqual(uri, '/admin/v2/groups/ABC123/users')
        self.assertEqual(
            util.params_to_dict(args),
            {
                'account_id': [self.client.account_id],
                'limit': ['100'],
                'offset': ['0'],
            })

    def test_get_group_users_with_offset(self):
        """Test to get users by group id with pagination params
        """
        response = self.client_list.get_group_users('ABC123', offset=30)[0]
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'GET')
        self.assertEqual(uri, '/admin/v2/groups/ABC123/users')
        self.assertEqual(util.params_to_dict(args),
                         {
                            'account_id':[self.client.account_id],
                            'limit': ['100'],
                            'offset': ['0'],
                         })

    def test_get_group_users_with_limit(self):
        """Test to get users by group id with pagination params
        """
        response = self.client_list.get_group_users('ABC123', limit=30)[0]
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'GET')
        self.assertEqual(uri, '/admin/v2/groups/ABC123/users')
        self.assertEqual(util.params_to_dict(args),
                         {
                            'account_id':[self.client.account_id],
                            'limit': ['30'],
                            'offset': ['0'],
                         })

    def test_get_group_users_with_limit_and_offset(self):
        """Test to get users by group id with pagination params
        """
        response = self.client_list.get_group_users(
            'ABC123', limit=30, offset=60)[0]
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'GET')
        self.assertEqual(uri, '/admin/v2/groups/ABC123/users')
        self.assertEqual(util.params_to_dict(args),
                         {
                            'account_id':[self.client.account_id],
                            'limit': ['30'],
                            'offset': ['60'],
                         })

    def test_get_group_users_iterator(self):
        """Test to get user iterator by group id
        """
        iterator = self.client_list.get_group_users_iterator(
            'ABC123')
        response = next(iterator)
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'GET')
        self.assertEqual(uri, '/admin/v2/groups/ABC123/users')
        self.assertEqual(util.params_to_dict(args),
                         {
                            'account_id':[self.client.account_id],
                            'limit': ['100'],
                            'offset': ['0'],
                         })

    def test_delete_group(self):
        """ Test for deleting a group
        """
        response = self.client.delete_group('ABC123')
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'DELETE')
        self.assertEqual(uri, '/admin/v1/groups/ABC123')
        self.assertEqual(util.params_to_dict(args),
                         {'account_id': [self.client.account_id]})

    def test_modify_group(self):
        """ Test for modifying a group
        """
        response = self.client.modify_group('ABC123')
        self.assertEqual(response['method'], 'POST')
        self.assertEqual(response['uri'], '/admin/v1/groups/ABC123')
        self.assertEqual(util.params_to_dict(response['body']),
                         {'account_id': [self.client.account_id]})
