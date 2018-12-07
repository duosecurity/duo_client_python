from .. import util
import duo_client.admin
from .base import TestAdmin


class TestTokens(TestAdmin):
    def test_get_tokens_generator(self):
        """ Test to get tokens generator.
        """
        generator = self.client_list.get_tokens_generator()
        response = next(generator)
        self.assertEqual(response['method'], 'GET')
        (uri, args) = response['uri'].split('?')
        self.assertEqual(uri, '/admin/v1/tokens')
        self.assertEqual(
            util.params_to_dict(args),
            {
                'account_id': [self.client.account_id],
                'limit': ['100'],
                'offset': ['0'],
            })

    def test_get_tokens(self):
        """ Test to get tokens without pagination params.
        """
        response = self.client_list.get_tokens()
        response = response[0]
        self.assertEqual(response['method'], 'GET')
        (uri, args) = response['uri'].split('?')
        self.assertEqual(uri, '/admin/v1/tokens')
        self.assertEqual(
            util.params_to_dict(args),
            {
                'account_id': [self.client.account_id],
                'limit': ['100'],
                'offset': ['0'],
            })

    def test_get_tokens_with_limit(self):
        """ Test to get tokens with pagination params.
        """
        response = self.client_list.get_tokens(limit=20)
        response = response[0]
        self.assertEqual(response['method'], 'GET')
        (uri, args) = response['uri'].split('?')
        self.assertEqual(uri, '/admin/v1/tokens')
        self.assertEqual(
            util.params_to_dict(args),
            {
                'account_id': [self.client.account_id],
                'limit': ['20'],
                'offset': ['0'],
            })

    def test_get_tokens_with_limit_offset(self):
        """ Test to get tokens with pagination params.
        """
        response = self.client_list.get_tokens(limit=20, offset=2)
        response = response[0]
        self.assertEqual(response['method'], 'GET')
        (uri, args) = response['uri'].split('?')
        self.assertEqual(uri, '/admin/v1/tokens')
        self.assertEqual(
            util.params_to_dict(args),
            {
                'account_id': [self.client.account_id],
                'limit': ['20'],
                'offset': ['2'],
            })

    def test_get_tokens_with_offset(self):
        """ Test to get tokens with pagination params.
        """
        response = self.client_list.get_tokens(offset=9001)
        response = response[0]
        self.assertEqual(response['method'], 'GET')
        (uri, args) = response['uri'].split('?')
        self.assertEqual(uri, '/admin/v1/tokens')
        self.assertEqual(
            util.params_to_dict(args),
            {
                'account_id': [self.client.account_id],
                'limit': ['100'],
                'offset': ['0'],
            })
