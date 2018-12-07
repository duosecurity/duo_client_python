from .. import util
import duo_client.admin
from .base import TestAdmin


class TestPhones(TestAdmin):
    def test_get_phones_generator(self):
        """ Test to get phones generator.
        """
        generator = self.client_list.get_phones_generator()
        response = next(generator)
        self.assertEqual(response['method'], 'GET')
        (uri, args) = response['uri'].split('?')
        self.assertEqual(uri, '/admin/v1/phones')
        self.assertEqual(
            util.params_to_dict(args),
            {
                'account_id': [self.client.account_id],
                'limit': ['100'],
                'offset': ['0'],
            })

    def test_get_phones(self):
        """ Test to get phones without pagination params.
        """
        response = self.client_list.get_phones()
        response = response[0]
        self.assertEqual(response['method'], 'GET')
        (uri, args) = response['uri'].split('?')
        self.assertEqual(uri, '/admin/v1/phones')
        self.assertEqual(
            util.params_to_dict(args),
            {
                'account_id': [self.client.account_id],
                'limit': ['100'],
                'offset': ['0'],
            })

    def test_get_phones_with_limit(self):
        """ Test to get phones with pagination params.
        """
        response = self.client_list.get_phones(limit=20)
        response = response[0]
        self.assertEqual(response['method'], 'GET')
        (uri, args) = response['uri'].split('?')
        self.assertEqual(uri, '/admin/v1/phones')
        self.assertEqual(
            util.params_to_dict(args),
            {
                'account_id': [self.client.account_id],
                'limit': ['20'],
                'offset': ['0'],
            })

    def test_get_phones_with_limit_offset(self):
        """ Test to get phones with pagination params.
        """
        response = self.client_list.get_phones(limit=20, offset=2)
        response = response[0]
        self.assertEqual(response['method'], 'GET')
        (uri, args) = response['uri'].split('?')
        self.assertEqual(uri, '/admin/v1/phones')
        self.assertEqual(
            util.params_to_dict(args),
            {
                'account_id': [self.client.account_id],
                'limit': ['20'],
                'offset': ['2'],
            })

    def test_get_phones_with_offset(self):
        """ Test to get phones with pagination params.
        """
        response = self.client_list.get_phones(offset=9001)
        response = response[0]
        self.assertEqual(response['method'], 'GET')
        (uri, args) = response['uri'].split('?')
        self.assertEqual(uri, '/admin/v1/phones')
        self.assertEqual(
            util.params_to_dict(args),
            {
                'account_id': [self.client.account_id],
                'limit': ['100'],
                'offset': ['0'],
            })
