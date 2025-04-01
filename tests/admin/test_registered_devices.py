import json

from .base import TestAdmin
from .. import util


class TestRegisteredDevices(TestAdmin):
    def test_get_registered_devices_generator(self):
        """ Test to get registered devices generator.
        """
        generator = self.client_list.get_registered_devices_generator()
        response = next(generator)
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'GET')
        self.assertEqual(uri, '/admin/v1/registered_devices')
        self.assertEqual(util.params_to_dict(args),
                {'account_id': [self.client_list.account_id], 'limit': ['100'], 'offset': ['0'], })

    def test_get_registered_devices(self):
        """ Test to get registered devices without params.
        """
        response = self.client_list.get_registered_devices()[0]
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'GET')
        self.assertEqual(uri, '/admin/v1/registered_devices')
        self.assertEqual(util.params_to_dict(args),
                {'account_id': [self.client_list.account_id], 'limit': ['100'], 'offset': ['0'], })

    def test_get_registered_devices_limit(self):
        """ Test to get registered devices with limit.
        """
        response = self.client_list.get_registered_devices(limit='20')[0]
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'GET')
        self.assertEqual(uri, '/admin/v1/registered_devices')
        self.assertEqual(util.params_to_dict(args),
                {'account_id': [self.client_list.account_id], 'limit': ['20'], 'offset': ['0'], })

    def test_get_registered_devices_offset(self):
        """ Test to get registered devices with offset.
        """
        response = self.client_list.get_registered_devices(offset='20')[0]
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'GET')
        self.assertEqual(uri, '/admin/v1/registered_devices')
        self.assertEqual(util.params_to_dict(args),
                {'account_id': [self.client_list.account_id], 'limit': ['100'], 'offset': ['0'], })

    def test_get_registered_devices_limit_offset(self):
        """ Test to get registered devices with limit and offset.
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

    def test_get_blocked_devices_generator(self):
        """ Test to get blocked devices generator.
        """
        generator = self.client_list.get_blocked_devices_generator()
        response = next(generator)
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'GET')
        self.assertEqual(uri, '/admin/v1/registered_devices/blocked')
        self.assertEqual(
            util.params_to_dict(args),
            {'account_id': [self.client_list.account_id], 'limit': ['100'], 'offset': ['0'], }
            )

    def test_get_blocked_devices(self):
        """ Test to get blocked devices without params.
        """
        response = self.client_list.get_blocked_devices()[0]
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'GET')
        self.assertEqual(uri, '/admin/v1/registered_devices/blocked')
        self.assertEqual(
            util.params_to_dict(args),
            {'account_id': [self.client_list.account_id], 'limit': ['100'], 'offset': ['0'], }
            )

    def test_get_blocked_devices_limit(self):
        """ Test to get blocked devices with limit.
        """
        response = self.client_list.get_blocked_devices(limit='20')[0]
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'GET')
        self.assertEqual(uri, '/admin/v1/registered_devices/blocked')
        self.assertEqual(
            util.params_to_dict(args),
            {'account_id': [self.client_list.account_id], 'limit': ['20'], 'offset': ['0'], }
            )

    def test_get_blocked_devices_offset(self):
        """ Test to get blocked devices with offset.
        """
        response = self.client_list.get_blocked_devices(offset='20')[0]
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'GET')
        self.assertEqual(uri, '/admin/v1/registered_devices/blocked')
        self.assertEqual(
            util.params_to_dict(args),
            {'account_id': [self.client_list.account_id], 'limit': ['100'], 'offset': ['0'], }
            )

    def test_get_blocked_devices_limit_offset(self):
        """ Test to get blocked devices with limit and offset.
        """
        response = self.client_list.get_blocked_devices(limit='20', offset='2')[0]
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'GET')
        self.assertEqual(uri, '/admin/v1/registered_devices/blocked')
        self.assertEqual(
            util.params_to_dict(args),
            {'account_id': [self.client_list.account_id], 'limit': ['20'], 'offset': ['2'], }
            )

    def test_block_registered_device_by_id(self):
        """ Test to block registered device by registered device id.
        """
        response = self.client.block_registered_device_by_id('CRSFWW1YWVNUXMBJ1J29')

        self.assertEqual(response['method'], 'POST')
        self.assertEqual(response['uri'], '/admin/v1/registered_devices/blocked/CRSFWW1YWVNUXMBJ1J29')
        self.assertEqual(json.loads(response['body'])['account_id'], self.client.account_id)

    def test_block_registered_devices(self):
        """ Test to block registered devices.
        """
        response = self.client.block_registered_devices(['CRSFWW1YWVNUXMBJ1J29', 'CRSFWW1YWVNUXMBJ1J30'])

        self.assertEqual(response['method'], 'POST')
        self.assertEqual(response['uri'], '/admin/v1/registered_devices/blocked')
        self.assertEqual(json.loads(response['body'])['account_id'], self.client.account_id)

    def test_unblock_registered_device_by_id(self):
        """ Test to unblock registered device by registered device id.
        """
        response = self.client.unblock_registered_device_by_id('CRSFWW1YWVNUXMBJ1J29')
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'DELETE')
        self.assertEqual(uri, '/admin/v1/registered_devices/blocked/CRSFWW1YWVNUXMBJ1J29')
        self.assertEqual(util.params_to_dict(args), {'account_id': [self.client.account_id]})

    def test_unblock_registered_devices(self):
        """ Test to unblock registered devices.
        """
        response = self.client.unblock_registered_devices(['CRSFWW1YWVNUXMBJ1J29', 'CRSFWW1YWVNUXMBJ1J30'])
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'DELETE')
        self.assertEqual(uri, '/admin/v1/registered_devices/blocked')
        self.assertEqual(util.params_to_dict(args)['account_id'], [self.client.account_id])
