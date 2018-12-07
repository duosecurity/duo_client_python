from .. import util
import duo_client.admin
from .base import TestAdmin


class TestDesktopTokens(TestAdmin):
    def test_get_desktoptokens_generator(self):
        """ Test to get desktop tokens generator.
        """
        generator = self.client_list.get_desktoptokens_generator()
        response = next(generator)
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'GET')
        self.assertEqual(uri, '/admin/v1/desktoptokens')
        self.assertEqual(
            util.params_to_dict(args),
            {
                'account_id': [self.client_list.account_id],
                'limit': ['100'],
                'offset': ['0'],
            })

    def test_get_desktoptokens(self):
        """ Test to get desktop tokens without params.
        """
        response = self.client_list.get_desktoptokens()[0]
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'GET')
        self.assertEqual(uri, '/admin/v1/desktoptokens')
        self.assertEqual(
            util.params_to_dict(args),
            {
                'account_id': [self.client_list.account_id],
                'limit': ['100'],
                'offset': ['0'],
            })

    def test_get_desktoptokens_limit(self):
        """ Test to get desktop tokens with limit.
        """
        response = self.client_list.get_desktoptokens(limit='20')[0]
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'GET')
        self.assertEqual(uri, '/admin/v1/desktoptokens')
        self.assertEqual(
            util.params_to_dict(args),
            {
                'account_id': [self.client_list.account_id],
                'limit': ['20'],
                'offset': ['0'],
            })

    def test_get_desktoptokens_offset(self):
        """ Test to get desktop tokens with offset.
        """
        response = self.client_list.get_desktoptokens(offset='20')[0]
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'GET')
        self.assertEqual(uri, '/admin/v1/desktoptokens')
        self.assertEqual(
            util.params_to_dict(args),
            {
                'account_id': [self.client_list.account_id],
                'limit': ['100'],
                'offset': ['0'],
            })

    def test_get_desktoptokens_limit_offset(self):
        """ Test to get desktop tokens with limit and offset.
        """
        response = self.client_list.get_desktoptokens(limit='20', offset='2')[0]
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'GET')
        self.assertEqual(uri, '/admin/v1/desktoptokens')
        self.assertEqual(
            util.params_to_dict(args),
            {
                'account_id': [self.client_list.account_id],
                'limit': ['20'],
                'offset': ['2'],
            })
