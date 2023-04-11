from .. import util
import duo_client.admin
from .base import TestAdmin


class TestPolicies(TestAdmin):
    def setUp(self):
        super(TestPolicies, self).setUp()
        self.client.account_id = None
        self.client_list.account_id = None

    def test_delete_policy_v2(self):
        policy_key = "POSTGY2G0HVWJR4JO1XT"
        response = self.client.delete_policy_v2(policy_key)
        uri, _ = response["uri"].split("?")

        self.assertEqual(response["method"], "DELETE")
        self.assertEqual(uri, "/admin/v2/policies/{}".format(policy_key))

    def test_get_policy_v2(self):
        policy_key = "POSTGY2G0HVWJR4JO1XT"
        response = self.client.get_policy_v2(policy_key)
        uri, _ = response["uri"].split("?")

        self.assertEqual(response["method"], "GET")
        self.assertEqual(uri, "/admin/v2/policies/{}".format(policy_key))

    def test_update_policy_v2(self):
        policy_key = "POSTGY2G0HVWJR4JO1XT"
        policy_settings = {
            "sections": {
                "browsers": {
                    "blocked_browsers_list": ["ie"],
                }
            }
        }
        response = self.client.update_policy_v2(policy_key, policy_settings)

        self.assertEqual(response["method"], "PUT")
        self.assertEqual(response["uri"], "/admin/v2/policies/{}".format(policy_key))

    def test_create_policy_v2(self):
        policy_settings = {
            "name": "my new policy",
            "sections": {
                "browsers": {
                    "blocked_browsers_list": ["ie"],
                }
            },
        }
        response = self.client.create_policy_v2(policy_settings)

        self.assertEqual(response["method"], "POST")
        self.assertEqual(response["uri"], "/admin/v2/policies")

    def test_get_policies_v2(self):
        response = self.client.get_policies_v2(limit=3, offset=0)
        uri, args = response["uri"].split("?")

        self.assertEqual(response["method"], "GET")
        self.assertEqual(uri, "/admin/v2/policies")
        self.assertDictEqual(
            util.params_to_dict(args), {"limit": ["3"], "offset": ["0"]}
        )

    def test_get_policies_v2_iterator(self):
        iterator = self.client_list.get_policies_v2_iterator()
        response = next(iterator)
        uri, args = response["uri"].split("?")

        self.assertEqual(response["method"], "GET")
        self.assertEqual(uri, "/admin/v2/policies")
        self.assertDictEqual(
            util.params_to_dict(args), {"limit": ["100"], "offset": ["0"]}
        )
