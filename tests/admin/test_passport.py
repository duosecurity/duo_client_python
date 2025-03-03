import json

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

    def test_update_passport(self):
        """ Test update passport configuration
        """
        response = self.client.update_passport_config(enabled_status="enabled-for-groups", enabled_groups=["passport-test-group"], custom_supported_browsers={"macos": [{"team_id": "UBF8T346G9"},], "windows": [{"common_name": "Duo Security LLC"},],})
        self.assertEqual(response["uri"], "/admin/v2/passport/config")
        body = json.loads(response["body"])
        self.assertEqual(body["enabled_status"], "enabled-for-groups")
        self.assertEqual(body["enabled_groups"], ["passport-test-group"])
        self.assertEqual(body["disabled_groups"], None)
        self.assertEqual(body["custom_supported_browsers"], {"macos":[{"team_id":"UBF8T346G9"}],"windows":[{"common_name":"Duo Security LLC"}]})
