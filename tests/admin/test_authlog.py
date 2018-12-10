from .. import util
import duo_client.admin
from .base import TestAdmin


class TestEndpoints(TestAdmin):
    def test_get_authentication_log_v1(self):
        """ Test to get authentication log on version 1 api.
        """
        response = self.client_list.get_authentication_log(api_version=1)[0]
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'GET')
        self.assertEqual(uri, '/admin/v1/logs/authentication')
        self.assertEqual(
            util.params_to_dict(args)['account_id'],
            [self.client_list.account_id])

    def test_get_authentication_log_v2(self):
        """ Test to get authentication log on version 1 api.
        """
        response = self.client_authlog.get_authentication_log(api_version=2)
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'GET')
        self.assertEqual(uri, '/admin/v2/logs/authentication')
        self.assertEqual(
            util.params_to_dict(args)['account_id'],
            [self.client_authlog.account_id])
