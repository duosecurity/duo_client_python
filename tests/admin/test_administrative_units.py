from .. import util
from .base import TestAdmin


class TestAdminUnits(TestAdmin):
    # Uses underlying paging
    def test_get_administratrive_units(self):
        response = self.client_list.get_administrative_units()
        response = response[0]
        self.assertEqual(response['method'], 'GET')
        (uri, args) = response['uri'].split('?')
        self.assertEqual(uri, '/admin/v1/administrative_units')

    def test_get_administrative_units_with_limit(self):
        response = self.client_list.get_administrative_units(limit=20)
        response = response[0]
        self.assertEqual(response['method'], 'GET')
        (uri, args) = response['uri'].split('?')
        self.assertEqual(uri, '/admin/v1/administrative_units')
        self.assertEqual(
            util.params_to_dict(args),
            {
                'account_id': [self.client.account_id],
                'limit': ['20'],
                'offset': ['0'],
            })

    def test_get_adminstrative_units_with_limit_offset(self):
        response = self.client_list.get_administrative_units(limit=20, offset=2)
        response = response[0]
        self.assertEqual(response['method'], 'GET')
        (uri, args) = response['uri'].split('?')
        self.assertEqual(uri, '/admin/v1/administrative_units')
        self.assertEqual(
            util.params_to_dict(args),
            {
                'account_id': [self.client.account_id],
                'limit': ['20'],
                'offset': ['2'],
            })

    def test_get_administrative_units_with_offset(self):
        response = self.client_list.get_administrative_units(offset=9001)
        response = response[0]
        self.assertEqual(response['method'], 'GET')
        (uri, args) = response['uri'].split('?')
        self.assertEqual(uri, '/admin/v1/administrative_units')
        self.assertEqual(
            util.params_to_dict(args),
            {
                'account_id': [self.client.account_id],
                'limit': ['100'],
                'offset': ['0'],
            })

    def test_get_administrative_units_iterator(self):
        expected_path = '/admin/v1/administrative_units'
        expected_method = 'GET'

        tests = [
            {
                'admin_id': 'aaaa',
                'group_id': '1234',
                'integration_key': 'aaaaaaaaaaaaaaaaaaaa',
            },
            {
                'admin_id': 'aaaa',
                'group_id': '1234',
            },
            {
                'admin_id': 'aaaa',
            },
            {}
        ]

        for test in tests:
            response = (
                self.client_list.get_administrative_units_iterator(**test)
            )
            response = next(response)
            self.assertEqual(response['method'], expected_method)
            (uri, args) = response['uri'].split('?')
            self.assertEqual(uri, expected_path)
            expected_params = {
                key: [value] for (key, value) in test.items()
            }
            expected_params.update(
                {
                    'account_id': [self.client.account_id],
                    'limit': ['100'],
                    'offset': ['0'],
                }
            )
            self.assertEqual(util.params_to_dict(args), expected_params)
