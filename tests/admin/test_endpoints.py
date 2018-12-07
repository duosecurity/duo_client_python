from .. import util
import duo_client.admin
from .base import TestAdmin


class TestEndpoints(TestAdmin):
    def test_get_endpoints(self):
        response = self.client.get_endpoints()
        self.assertEqual(response['method'], 'GET')
        (uri, args) = response['uri'].split('?')
        self.assertEqual(uri, '/admin/v1/endpoints')
        self.assertEqual(
            util.params_to_dict(args),
            {'account_id': [self.client.account_id]})
