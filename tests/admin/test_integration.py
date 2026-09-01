import unittest

from .. import util
import json
import duo_client.admin
from .base import TestAdmin

SUBACCOUNT_PERMISSIONS = [
    'adminapi_subaccount_accounts',
    'adminapi_subaccount_accounts_read',
    'adminapi_subaccount_admins',
    'adminapi_subaccount_admins_read',
    'adminapi_subaccount_info',
    'adminapi_subaccount_integrations',
    'adminapi_subaccount_integrations_read',
    'adminapi_subaccount_settings',
    'adminapi_subaccount_settings_read',
    'adminapi_subaccount_read_log',
    'adminapi_subaccount_read_resource',
    'adminapi_subaccount_write_resource',
    'adminapi_subaccount_allow_to_set_permissions',
    'adminapi_subaccount_user_limits',
    'adminapi_subaccount_user_limits_read',
]


class TestIntegration(TestAdmin):
    def setUp(self):
        super(TestIntegration, self).setUp()
        self.integration_key = "DISRYL7L8LZ5YXNWKGNK"

    def test_get_integration(self):
        response = self.client.get_integration(self.integration_key)
        (uri, args) = response['uri'].split('?')

        self.assertEqual(response['method'], 'GET')
        self.assertEqual(uri, '/admin/v3/integrations/{}'.format(self.integration_key))
        self.assertEqual(util.params_to_dict(args), {'account_id': [self.client.account_id]})

    def test_delete_integration(self):
        response = self.client.delete_integration(self.integration_key)
        (uri, args) = response['uri'].split('?')

        self.assertEqual(response['method'], 'DELETE')
        self.assertEqual(uri, '/admin/v3/integrations/{}'.format(self.integration_key))
        self.assertEqual(util.params_to_dict(args), {'account_id': [self.client.account_id]})

    def test_create_integration(self):
        response = self.client.create_integration(
            name="New integration name",
            integration_type="sso-generic",
            sso={
                "idp_metadata": None,
                "saml_config": {}
            },
        )

        self.assertEqual(response['method'], 'POST')
        self.assertEqual(response['uri'], '/admin/v3/integrations')
        self.assertEqual(json.loads(response['body']),
            {
                "account_id": self.client.account_id,
                "name": "New integration name",
                "type": "sso-generic",
                "sso": {
                    "idp_metadata": None,
                    "saml_config": {}
                },
            }
        )

    def test_create_integration_subaccount_permissions(self):
        response = self.client.create_integration(
            name="Subaccount integration",
            integration_type="adminapi",
            **{perm: True for perm in SUBACCOUNT_PERMISSIONS}
        )

        expected = {
            "account_id": self.client.account_id,
            "name": "Subaccount integration",
            "type": "adminapi",
        }
        expected.update({perm: "1" for perm in SUBACCOUNT_PERMISSIONS})

        self.assertEqual(response['method'], 'POST')
        self.assertEqual(response['uri'], '/admin/v3/integrations')
        self.assertEqual(json.loads(response['body']), expected)

    def test_update_integration_subaccount_permissions(self):
        response = self.client.update_integration(
            self.integration_key,
            **{perm: False for perm in SUBACCOUNT_PERMISSIONS}
        )

        expected = {"account_id": self.client.account_id}
        expected.update({perm: "0" for perm in SUBACCOUNT_PERMISSIONS})

        self.assertEqual(response['method'], 'POST')
        self.assertEqual(
            response['uri'],
            '/admin/v3/integrations/{}'.format(self.integration_key))
        self.assertEqual(json.loads(response['body']), expected)

    def test_update_integration_success(self):
        response = self.client.update_integration(
            self.integration_key,
            name="Integration name",
            sso={
                "saml_config": {
                    "nameid_attribute": "mail",
                }
            },
        )

        self.assertEqual(response['method'], 'POST')
        self.assertEqual(response['uri'], '/admin/v3/integrations/{}'.format(self.integration_key))
        self.assertEqual(json.loads(response['body']),
            {
                "account_id": self.client.account_id,
                "name": "Integration name",
                "sso": {
                    "saml_config": {
                        "nameid_attribute": "mail",
                    }
                },
            }
        )

if __name__ == '__main__':
    unittest.main()
