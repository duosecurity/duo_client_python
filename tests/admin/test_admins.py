from .. import util
import duo_client.admin
from .base import TestAdmin


class TestAdmins(TestAdmin):
    # Uses underlying paging
    def test_get_admins(self):
        response = self.client_list.get_admins()
        response = response[0]
        self.assertEqual(response['method'], 'GET')
        (uri, args) = response['uri'].split('?')
        self.assertEqual(uri, '/admin/v1/admins')
        self.assertEqual(
            util.params_to_dict(args),
            {
                'account_id': [self.client.account_id],
                'limit': ['100'],
                'offset': ['0'],
            })

    def test_get_admins_with_limit(self):
        response = self.client_list.get_admins(limit='20')
        response = response[0]
        self.assertEqual(response['method'], 'GET')
        (uri, args) = response['uri'].split('?')
        self.assertEqual(uri, '/admin/v1/admins')
        self.assertEqual(
            util.params_to_dict(args),
            {
                'account_id': [self.client.account_id],
                'limit': ['20'],
                'offset': ['0'],
            })

    def test_get_admins_with_limit_offset(self):
        response = self.client_list.get_admins(limit='20', offset='2')
        response = response[0]
        self.assertEqual(response['method'], 'GET')
        (uri, args) = response['uri'].split('?')
        self.assertEqual(uri, '/admin/v1/admins')
        self.assertEqual(
            util.params_to_dict(args),
            {
                'account_id': [self.client.account_id],
                'limit': ['20'],
                'offset': ['2'],
            })

    def test_get_admins_with_offset(self):
        response = self.client_list.get_admins(offset=9001)
        response = response[0]
        self.assertEqual(response['method'], 'GET')
        (uri, args) = response['uri'].split('?')
        self.assertEqual(uri, '/admin/v1/admins')
        self.assertEqual(
            util.params_to_dict(args),
            {
                'account_id': [self.client.account_id],
                'limit': ['100'],
                'offset': ['0'],
            })

    def test_get_admins_iterator(self):
        response = self.client_list.get_admins_iterator()
        response = next(response)
        self.assertEqual(response['method'], 'GET')
        (uri, args) = response['uri'].split('?')
        self.assertEqual(uri, '/admin/v1/admins')
        self.assertEqual(
            util.params_to_dict(args),
            {
                'account_id': [self.client.account_id],
                'limit': ['100'],
                'offset': ['0'],
            })
