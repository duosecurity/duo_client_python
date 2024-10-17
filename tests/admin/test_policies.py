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

    def test_update_policies_v2(self):
        edit_list = ["POSTGY2G0HVWJR4JO1XT", "POSTGY2G0HVWJR4JO1XU"]
        sections = {
                "browsers": {
                    "blocked_browsers_list": ["ie"],
                }
        }
        response = self.client.update_policies_v2(sections, [], edit_list)
        self.assertEqual(response["method"], "PUT")
        self.assertEqual(response["uri"], "/admin/v2/policies/update")

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

    def test_copy_policy_v2(self):
        policy_key = "POSTGY2G0HVWJR4JO1XT"
        new_policy_names_list = ["Copied Pol 1", "Copied Pol 2"]
        response = self.client.copy_policy_v2(policy_key, new_policy_names_list)

        self.assertEqual(response["method"], "POST")
        self.assertEqual(response["uri"], "/admin/v2/policies/copy")

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

    def test_get_policy_summary(self):
        response = self.client.get_policy_summary_v2()
        uri, _ = response["uri"].split("?")

        self.assertEqual(response["method"], "GET")
        self.assertEqual(uri, "/admin/v2/policies/summary")

    def test_calculate_policy(self):
        ikey = "DI82WWNVI5Z4V10LZJR6"
        ukey = "DUQU89MDEWOUR277H44G"

        response = self.client.calculate_policy(integration_key=ikey, user_id=ukey)
        uri, args = response["uri"].split("?")

        self.assertEqual(response["method"], "GET")
        self.assertEqual(uri, "/admin/v2/policies/calculate")
        self.assertDictEqual(
            util.params_to_dict(args), {"integration_key": [ikey], "user_id": [ukey]}
        )