from .base import TestAdmin
from .. import util


class TestPassport(TestAdmin):
    def test_get_passport(self):
        """ Test get passport configuration
        """
        response = self.client.get_passport_config()
        (uri, args) = response['uri'].split('?')
        self.assertEqual(response['method'], 'GET')
        self.assertEqual(uri, '/admin/v2/passport/config')
        self.assertEqual(util.params_to_dict(args), {'account_id': [self.client.account_id]})
