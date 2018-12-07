import duo_client.admin
from .. import util
from .base import TestAdmin


class TestBypassCodes(TestAdmin):
    def test_delete_bypass_code_by_id(self):
        """ Test to delete a bypass code by id.
        """
        response = self.client.delete_bypass_code_by_id('DU012345678901234567')
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'DELETE')
        self.assertEqual(uri, '/admin/v1/bypass_codes/DU012345678901234567')
        self.assertEqual(util.params_to_dict(args),
                         {'account_id': [self.client.account_id]})

    def test_get_bypass_codes_generator(self):
        """ Test to get bypass codes generator.
        """
        generator = self.client_list.get_bypass_codes_generator()
        response = next(generator)
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'GET')
        self.assertEqual(uri, '/admin/v1/bypass_codes')
        self.assertEqual(
            util.params_to_dict(args),
            {
                'account_id': [self.client_list.account_id],
                'limit': ['100'],
                'offset': ['0'],
             })

    def test_get_bypass_codes(self):
        """ Test to get bypass codes without params.
        """
        response = self.client_list.get_bypass_codes()[0]
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'GET')
        self.assertEqual(uri, '/admin/v1/bypass_codes')
        self.assertEqual(
            util.params_to_dict(args),
            {
                'account_id': [self.client_list.account_id],
                'limit': ['100'],
                'offset': ['0'],
             })

    def test_get_bypass_codes_limit(self):
        """ Test to get bypass codes with limit.
        """
        response = self.client_list.get_bypass_codes(limit='20')[0]
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'GET')
        self.assertEqual(uri, '/admin/v1/bypass_codes')
        self.assertEqual(
            util.params_to_dict(args),
            {
                'account_id': [self.client_list.account_id],
                'limit': ['20'],
                'offset': ['0'],
            })

    def test_get_bypass_codes_offset(self):
        """ Test to get bypass codes with offset.
        """
        response = self.client_list.get_bypass_codes(offset='20')[0]
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'GET')
        self.assertEqual(uri, '/admin/v1/bypass_codes')
        self.assertEqual(
            util.params_to_dict(args),
            {
                'account_id': [self.client_list.account_id],
                'limit': ['100'],
                'offset': ['0'],
            })

    def test_get_bypass_codes_limit_offset(self):
        """ Test to get bypass codes with limit and offset.
        """
        response = self.client_list.get_bypass_codes(limit='20', offset='2')[0]
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'GET')
        self.assertEqual(uri, '/admin/v1/bypass_codes')
        self.assertEqual(
            util.params_to_dict(args),
            {
                'account_id': [self.client_list.account_id],
                'limit': ['20'],
                'offset': ['2'],
            })
