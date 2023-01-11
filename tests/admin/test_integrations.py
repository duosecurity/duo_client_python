from .. import util
import duo_client.admin
from .base import TestAdmin


class TestIntegrations(TestAdmin):
    def test_get_integrations_generator(self):
        """ Test to get integrations generator.
        """
        generator = self.client_list.get_integrations_generator()
        response = next(generator)
        self.assertEqual(response['method'], 'GET')
        (uri, args) = response['uri'].split('?')
        self.assertEqual(uri, '/admin/v2/integrations')
        self.assertEqual(
            util.params_to_dict(args),
            {
                'account_id': [self.client.account_id],
                'limit': ['100'],
                'offset': ['0'],
            })

    def test_get_integrations(self):
        """ Test to get integrations without pagination params.
        """
        response = self.client_list.get_integrations()
        response = response[0]
        self.assertEqual(response['method'], 'GET')
        (uri, args) = response['uri'].split('?')
        self.assertEqual(uri, '/admin/v2/integrations')
        self.assertEqual(
            util.params_to_dict(args),
            {
                'account_id': [self.client.account_id],
                'limit': ['100'],
                'offset': ['0'],
            })

    def test_get_integrations_with_limit(self):
        """ Test to get integrations with pagination params.
        """
        response = self.client_list.get_integrations(limit=20)
        response = response[0]
        self.assertEqual(response['method'], 'GET')
        (uri, args) = response['uri'].split('?')
        self.assertEqual(uri, '/admin/v2/integrations')
        self.assertEqual(
            util.params_to_dict(args),
            {
                'account_id': [self.client.account_id],
                'limit': ['20'],
                'offset': ['0'],
            })

    def test_get_integrations_with_limit_offset(self):
        """ Test to get integrations with pagination params.
        """
        response = self.client_list.get_integrations(limit=20, offset=2)
        response = response[0]
        self.assertEqual(response['method'], 'GET')
        (uri, args) = response['uri'].split('?')
        self.assertEqual(uri, '/admin/v2/integrations')
        self.assertEqual(
            util.params_to_dict(args),
            {
                'account_id': [self.client.account_id],
                'limit': ['20'],
                'offset': ['2'],
            })

    def test_get_integrations_with_offset(self):
        """ Test to get integrations with pagination params.
        """
        response = self.client_list.get_integrations(offset=9001)
        response = response[0]
        self.assertEqual(response['method'], 'GET')
        (uri, args) = response['uri'].split('?')
        self.assertEqual(uri, '/admin/v2/integrations')
        self.assertEqual(
            util.params_to_dict(args),
            {
                'account_id': [self.client.account_id],
                'limit': ['100'],
                'offset': ['0'],
            })
