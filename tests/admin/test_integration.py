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
        self.assertEqual(uri, '/admin/v2/integrations/{}'.format(self.integration_key))
        self.assertEqual(util.params_to_dict(args), {'account_id': [self.client.account_id]})

    def test_delete_integration(self):
        response = self.client.delete_integration(self.integration_key)
        (uri, args) = response['uri'].split('?')

        self.assertEqual(response['method'], 'DELETE')
        self.assertEqual(uri, '/admin/v2/integrations/{}'.format(self.integration_key))
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
        self.assertEqual(response['uri'], '/admin/v2/integrations')
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
        self.assertEqual(response['uri'], '/admin/v2/integrations/{}'.format(self.integration_key))
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