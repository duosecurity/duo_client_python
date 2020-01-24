from .. import util
import duo_client.admin
from .base import TestAdmin


class TestWebauthn(TestAdmin):
    def test_get_webauthncredentials_with_params(self):
        """ Test to get webauthn credentials with params.
        """
        response = list(self.client_list.get_webauthncredentials(limit=8))[0]
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'GET')
        self.assertEqual(uri, '/admin/v1/webauthncredentials')
        self.assertEqual(
            util.params_to_dict(args),
            {
                'account_id':[self.client_list.account_id],
                'limit': ['8'],
                'offset': ['0'],
            }
        )

    def test_get_webauthncredentials_iterator(self):
        response = self.client_list.get_webauthncredentials_iterator()
        response = next(response)
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'GET')
        self.assertEqual(uri, '/admin/v1/webauthncredentials')
        self.assertEqual(
            util.params_to_dict(args),
            {
                'account_id': [self.client_list.account_id],
                'limit': ['100'],
                'offset': ['0']
            }
        )

    def test_get_webauthncredentials_without_params(self):
        """ Test to get webauthn credentials without params.
        """
        response = list(self.client_list.get_webauthncredentials())[0]
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'GET')
        self.assertEqual(uri, '/admin/v1/webauthncredentials')
        self.assertEqual(
            util.params_to_dict(args),
            {
                'account_id': [self.client_list.account_id],
                'limit': ['100'],
                'offset': ['0'],
             }
        )

    def test_get_webauthncredentials_with_offset(self):
        response = list(self.client_list.get_webauthncredentials(limit=2, offset=3))[0]
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'GET')
        self.assertEqual(uri, '/admin/v1/webauthncredentials')
        self.assertEqual(
            util.params_to_dict(args),
            {
                'account_id':[self.client_list.account_id],
                'limit': ['2'],
                'offset': ['3']
            }
        )

    def test_get_webauthncredential_by_id(self):
        """ Test to get webauthn credential by registration id.
        """
        response = self.client.get_webauthncredential_by_id('DU012345678901234567')
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'GET')
        self.assertEqual(uri, '/admin/v1/webauthncredentials/DU012345678901234567')
        self.assertEqual(util.params_to_dict(args),
                         {'account_id':[self.client.account_id]})

    def test_delete_webauthncredential(self):
        """ Test to delete webauthn credential by registration id.
        """
        response = self.client.delete_webauthncredential('DU012345678901234567')
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'DELETE')
        self.assertEqual(uri, '/admin/v1/webauthncredentials/DU012345678901234567')
        self.assertEqual(util.params_to_dict(args),
                         {'account_id':[self.client.account_id]})