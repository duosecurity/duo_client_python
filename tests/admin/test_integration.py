import unittest

from .. import util
import json
import duo_client.admin
from .base import TestAdmin


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

    def test_create_integration_with_permissions(self):
        response = self.client.create_integration(
            name="Admin API integration",
            integration_type="adminapi",
            adminapi_admins=True,
            adminapi_admins_read=True,
            adminapi_info=True,
            adminapi_integrations=True,
            adminapi_integrations_read=True,
            adminapi_read_log=True,
            adminapi_read_resource=True,
            adminapi_settings=True,
            adminapi_settings_read=True,
            adminapi_write_resource=True,
            adminapi_allow_to_set_permissions=True,
            self_service_allowed=True,
        )

        self.assertEqual(response['method'], 'POST')
        self.assertEqual(response['uri'], '/admin/v3/integrations')
        self.assertEqual(json.loads(response['body']),
            {
                "account_id": self.client.account_id,
                "name": "Admin API integration",
                "type": "adminapi",
                "adminapi_admins": "1",
                "adminapi_admins_read": "1",
                "adminapi_info": "1",
                "adminapi_integrations": "1",
                "adminapi_integrations_read": "1",
                "adminapi_read_log": "1",
                "adminapi_read_resource": "1",
                "adminapi_settings": "1",
                "adminapi_settings_read": "1",
                "adminapi_write_resource": "1",
                "adminapi_allow_to_set_permissions": "1",
                "self_service_allowed": "1",
            }
        )

    def test_create_integration_with_permissions_disabled(self):
        response = self.client.create_integration(
            name="Admin API integration",
            integration_type="adminapi",
            adminapi_admins=False,
            adminapi_admins_read=False,
            adminapi_integrations_read=False,
            adminapi_settings_read=False,
            adminapi_allow_to_set_permissions=False,
        )

        self.assertEqual(response['method'], 'POST')
        self.assertEqual(response['uri'], '/admin/v3/integrations')
        self.assertEqual(json.loads(response['body']),
            {
                "account_id": self.client.account_id,
                "name": "Admin API integration",
                "type": "adminapi",
                "adminapi_admins": "0",
                "adminapi_admins_read": "0",
                "adminapi_integrations_read": "0",
                "adminapi_settings_read": "0",
                "adminapi_allow_to_set_permissions": "0",
            }
        )

    def test_update_integration_with_permissions(self):
        response = self.client.update_integration(
            self.integration_key,
            adminapi_admins=True,
            adminapi_admins_read=True,
            adminapi_info=True,
            adminapi_integrations=True,
            adminapi_integrations_read=True,
            adminapi_read_log=True,
            adminapi_read_resource=True,
            adminapi_settings=True,
            adminapi_settings_read=True,
            adminapi_write_resource=True,
            self_service_allowed=True,
        )

        self.assertEqual(response['method'], 'POST')
        self.assertEqual(response['uri'], '/admin/v3/integrations/{}'.format(self.integration_key))
        self.assertEqual(json.loads(response['body']),
            {
                "account_id": self.client.account_id,
                "adminapi_admins": "1",
                "adminapi_admins_read": "1",
                "adminapi_info": "1",
                "adminapi_integrations": "1",
                "adminapi_integrations_read": "1",
                "adminapi_read_log": "1",
                "adminapi_read_resource": "1",
                "adminapi_settings": "1",
                "adminapi_settings_read": "1",
                "adminapi_write_resource": "1",
                "self_service_allowed": "1",
            }
        )

    def test_update_integration_with_permissions_disabled(self):
        response = self.client.update_integration(
            self.integration_key,
            adminapi_admins_read=False,
            adminapi_integrations_read=False,
            adminapi_settings_read=False,
        )

        self.assertEqual(response['method'], 'POST')
        self.assertEqual(response['uri'], '/admin/v3/integrations/{}'.format(self.integration_key))
        self.assertEqual(json.loads(response['body']),
            {
                "account_id": self.client.account_id,
                "adminapi_admins_read": "0",
                "adminapi_integrations_read": "0",
                "adminapi_settings_read": "0",
            }
        )

if __name__ == '__main__':
    unittest.main()
