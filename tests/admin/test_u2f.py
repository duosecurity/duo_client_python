from .. import util
import duo_client.admin
from .base import TestAdmin


class TestU2F(TestAdmin):
    def test_get_u2ftokens_with_params(self):
        """ Test to get u2ftokens with params.
        """
        response = list(self.client_list.get_u2ftokens(limit=8))[0]
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'GET')
        self.assertEqual(uri, '/admin/v1/u2ftokens')
        self.assertEqual(
            util.params_to_dict(args),
            {
                'account_id':[self.client_list.account_id],
                'limit': ['8'],
                'offset': ['0'],
            }
        )

    def test_get_u2ftokens_iterator(self):
        response = self.client_list.get_u2ftokens_iterator()
        response = next(response)
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'GET')
        self.assertEqual(uri, '/admin/v1/u2ftokens')
        self.assertEqual(
            util.params_to_dict(args),
            {
                'account_id': [self.client_list.account_id],
                'limit': ['100'],
                'offset': ['0']
            }
        )

    def test_get_u2ftokens_without_params(self):
        """ Test to get u2ftokens without params.
        """
        response = list(self.client_list.get_u2ftokens())[0]
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'GET')
        self.assertEqual(uri, '/admin/v1/u2ftokens')
        self.assertEqual(
            util.params_to_dict(args),
            {
                'account_id': [self.client_list.account_id],
                'limit': ['100'],
                'offset': ['0'],
             }
        )

    def test_get_u2ftokens_with_offset(self):
        response = list(self.client_list.get_u2ftokens(limit=2, offset=3))[0]
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'GET')
        self.assertEqual(uri, '/admin/v1/u2ftokens')
        self.assertEqual(
            util.params_to_dict(args),
            {
                'account_id':[self.client_list.account_id],
                'limit': ['2'],
                'offset': ['3']
            }
        )

    def test_get_u2ftoken_by_id(self):
        """ Test to get u2ftoken by registration id.
        """
        response = self.client.get_u2ftoken_by_id('DU012345678901234567')
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'GET')
        self.assertEqual(uri, '/admin/v1/u2ftokens/DU012345678901234567')
        self.assertEqual(util.params_to_dict(args),
                         {'account_id':[self.client.account_id]})

    def test_delete_u2ftoken(self):
        """ Test to delete u2ftoken by registration id.
        """
        response = self.client.delete_u2ftoken('DU012345678901234567')
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'DELETE')
        self.assertEqual(uri, '/admin/v1/u2ftokens/DU012345678901234567')
        self.assertEqual(util.params_to_dict(args),
                         {'account_id':[self.client.account_id]})
