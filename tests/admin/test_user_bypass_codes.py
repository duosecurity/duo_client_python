from .. import util
import duo_client.admin
from .base import TestAdmin


class TestUserBypassCodes(TestAdmin):
    def test_get_user_bypass_codes(self):
        """ Test to get bypass codes by user id.
        """
        response = self.client_list.get_user_bypass_codes(
            'DU012345678901234567')[0]
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'GET')
        self.assertEqual(
            uri,
            '/admin/v1/users/DU012345678901234567/bypass_codes')
        self.assertEqual(
            util.params_to_dict(args),
            {
                'account_id': [self.client.account_id],
                'limit': ['100'],
                'offset': ['0'],
            })

    def test_get_user_bypass_codes_iterator(self):
        """ Test to get bypass codes iterator by user id.
        """
        iterator = self.client_list.get_user_bypass_codes_iterator(
            'DU012345678901234567')
        response = next(iterator)
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'GET')
        self.assertEqual(
            uri,
            '/admin/v1/users/DU012345678901234567/bypass_codes')
        self.assertEqual(
            util.params_to_dict(args),
            {
                'account_id': [self.client.account_id],
                'limit': ['100'],
                'offset': ['0'],
            })

    def test_get_user_bypass_codes_with_offset(self):
        """ Test to get bypass codes by user id with pagination params.
        """
        response = self.client_list.get_user_bypass_codes(
            'DU012345678901234567', offset=30)[0]
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'GET')
        self.assertEqual(
            uri,
            '/admin/v1/users/DU012345678901234567/bypass_codes')
        self.assertEqual(util.params_to_dict(args),
                         {
                            'account_id': [self.client.account_id],
                            'limit': ['100'],
                            'offset': ['0'],
                         })

    def test_get_user_bypass_codes_with_limit(self):
        """ Test to get bypass codes by user id with pagination params.
        """
        response = self.client_list.get_user_bypass_codes(
            'DU012345678901234567', limit=10)[0]
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'GET')
        self.assertEqual(
            uri,
            '/admin/v1/users/DU012345678901234567/bypass_codes')
        self.assertEqual(util.params_to_dict(args),
                         {
                            'account_id': [self.client.account_id],
                            'limit': ['10'],
                            'offset': ['0'],
                         })

    def test_get_user_bypass_codes_with_limit_and_offset(self):
        """ Test to get bypass codes by user id with pagination params.
        """
        response = self.client_list.get_user_bypass_codes(
            'DU012345678901234567', limit=10, offset=30)[0]
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'GET')
        self.assertEqual(
            uri,
            '/admin/v1/users/DU012345678901234567/bypass_codes')
        self.assertEqual(util.params_to_dict(args),
                         {
                            'account_id': [self.client.account_id],
                            'limit': ['10'],
                            'offset': ['30'],
                         })
