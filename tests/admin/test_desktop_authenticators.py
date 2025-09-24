from .base import TestAdmin
from .. import util


class TestDesktopAuthenticators(TestAdmin):
    def test_get_desktop_authenticators_generator(self):
        """ Test to get desktop authenticators generator.
        """
        generator = self.client_list.get_desktop_authenticators_generator()
        response = next(generator)
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'GET')
        self.assertEqual(uri, '/admin/v1/desktop_authenticators')
        self.assertEqual(util.params_to_dict(args),
                {'account_id': [self.client_list.account_id], 'limit': ['100'], 'offset': ['0'], })

    def test_get_desktop_authenticators(self):
        """ Test to get desktop authenticators without params.
        """
        response = self.client_list.get_desktop_authenticators()[0]
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'GET')
        self.assertEqual(uri, '/admin/v1/desktop_authenticators')
        self.assertEqual(util.params_to_dict(args),
                {'account_id': [self.client_list.account_id], 'limit': ['100'], 'offset': ['0'], })

    def test_get_desktop_authenticators_limit(self):
        """ Test to get desktop authenticators with limit.
        """
        response = self.client_list.get_desktop_authenticators(limit='20')[0]
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'GET')
        self.assertEqual(uri, '/admin/v1/desktop_authenticators')
        self.assertEqual(util.params_to_dict(args),
                {'account_id': [self.client_list.account_id], 'limit': ['20'], 'offset': ['0'], })

    def test_get_desktop_authenticators_offset(self):
        """ Test to get desktop authenticators with offset.
        """
        response = self.client_list.get_desktop_authenticators(offset='20')[0]
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'GET')
        self.assertEqual(uri, '/admin/v1/desktop_authenticators')
        self.assertEqual(util.params_to_dict(args),
                {'account_id': [self.client_list.account_id], 'limit': ['100'], 'offset': ['0'], })

    def test_get_desktop_authenticators_limit_offset(self):
        """ Test to get desktop authenticators with limit and offset.
        """
        response = self.client_list.get_desktop_authenticators(limit='20', offset='2')[0]
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'GET')
        self.assertEqual(uri, '/admin/v1/desktop_authenticators')
        self.assertEqual(util.params_to_dict(args),
                {'account_id': [self.client_list.account_id], 'limit': ['20'], 'offset': ['2'], })
