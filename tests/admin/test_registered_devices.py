from .base import TestAdmin
from .. import util


class TestRegisteredDevices(TestAdmin):
    def test_get_registered_devices_generator(self):
        """ Test to get desktop tokens generator.
        """
        generator = self.client_list.get_registered_devices_generator()
        response = next(generator)
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'GET')
        self.assertEqual(uri, '/admin/v1/registered_devices')
        self.assertEqual(util.params_to_dict(args),
                {'account_id': [self.client_list.account_id], 'limit': ['100'], 'offset': ['0'], })

    def test_get_registered_devices(self):
        """ Test to get desktop tokens without params.
        """
        response = self.client_list.get_registered_devices()[0]
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'GET')
        self.assertEqual(uri, '/admin/v1/registered_devices')
        self.assertEqual(util.params_to_dict(args),
                {'account_id': [self.client_list.account_id], 'limit': ['100'], 'offset': ['0'], })

    def test_get_registered_devices_limit(self):
        """ Test to get desktop tokens with limit.
        """
        response = self.client_list.get_registered_devices(limit='20')[0]
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'GET')
        self.assertEqual(uri, '/admin/v1/registered_devices')
        self.assertEqual(util.params_to_dict(args),
                {'account_id': [self.client_list.account_id], 'limit': ['20'], 'offset': ['0'], })

    def test_get_registered_devices_offset(self):
        """ Test to get desktop tokens with offset.
        """
        response = self.client_list.get_registered_devices(offset='20')[0]
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'GET')
        self.assertEqual(uri, '/admin/v1/registered_devices')
        self.assertEqual(util.params_to_dict(args),
                {'account_id': [self.client_list.account_id], 'limit': ['100'], 'offset': ['0'], })

    def test_get_registered_devices_limit_offset(self):
        """ Test to get desktop tokens with limit and offset.
        """
        response = self.client_list.get_registered_devices(limit='20', offset='2')[0]
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'GET')
        self.assertEqual(uri, '/admin/v1/registered_devices')
        self.assertEqual(util.params_to_dict(args),
                {'account_id': [self.client_list.account_id], 'limit': ['20'], 'offset': ['2'], })

    def test_delete_registered_device(self):
        """ Test to delete registered device by registered device id.
        """
        response = self.client.delete_registered_device('CRSFWW1YWVNUXMBJ1J29')
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'DELETE')
        self.assertEqual(uri, '/admin/v1/registered_devices/CRSFWW1YWVNUXMBJ1J29')
        self.assertEqual(util.params_to_dict(args), {'account_id': [self.client.account_id]})
