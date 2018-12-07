from .. import util
import duo_client.admin
from .base import TestAdmin


class TestEndpoints(TestAdmin):
    def test_get_endpoints_iterator(self):
        """ Test to get endpoints iterator
        """
        iterator = self.client_list.get_endpoints_iterator()
        response = next(iterator)
        self.assertEqual(response['method'], 'GET')
        (uri, args) = response['uri'].split('?')
        self.assertEqual(uri, '/admin/v1/endpoints')
        self.assertEqual(
            util.params_to_dict(args),
            {
                'account_id': [self.client.account_id],
                'limit': ['100'],
                'offset': ['0'],
            })

    def test_get_endpoints(self):
        """ Test to get endpoints.
        """
        response = self.client_list.get_endpoints()[0]
        self.assertEqual(response['method'], 'GET')
        (uri, args) = response['uri'].split('?')
        self.assertEqual(uri, '/admin/v1/endpoints')
        self.assertEqual(
            util.params_to_dict(args),
            {
                'account_id': [self.client.account_id],
                'limit': ['100'],
                'offset': ['0'],
            })

    def test_get_endpoints_offset(self):
        """ Test to get endpoints with pagination params.
        """
        response = self.client_list.get_endpoints(offset=20)[0]
        self.assertEqual(response['method'], 'GET')
        (uri, args) = response['uri'].split('?')
        self.assertEqual(uri, '/admin/v1/endpoints')
        self.assertEqual(
            util.params_to_dict(args),
            {
                'account_id': [self.client.account_id],
                'limit': ['100'],
                'offset': ['0'],
            })

    def test_get_endpoints_limit(self):
        """ Test to get endpoints with pagination params.
        """
        response = self.client_list.get_endpoints(limit=20)[0]
        self.assertEqual(response['method'], 'GET')
        (uri, args) = response['uri'].split('?')
        self.assertEqual(uri, '/admin/v1/endpoints')
        self.assertEqual(
            util.params_to_dict(args),
            {
                'account_id': [self.client.account_id],
                'limit': ['20'],
                'offset': ['0'],
            })

    def test_get_endpoints_limit_and_offset(self):
        """ Test to get endpoints with pagination params.
        """
        response = self.client_list.get_endpoints(limit=35, offset=20)[0]
        self.assertEqual(response['method'], 'GET')
        (uri, args) = response['uri'].split('?')
        self.assertEqual(uri, '/admin/v1/endpoints')
        self.assertEqual(
            util.params_to_dict(args),
            {
                'account_id': [self.client.account_id],
                'limit': ['35'],
                'offset': ['20'],
            })


if __name__ == '__main__':
    unittest.main()
