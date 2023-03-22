import json

from .. import util
import duo_client.admin
from .base import TestAccountAdmin


class TestBilling(TestAccountAdmin):
    def test_get_billing_edition(self):
        """Test to get billing edition
        """
        response = self.client.get_edition()
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'GET')
        self.assertEqual(uri, '/admin/v1/billing/edition')
        self.assertEqual(util.params_to_dict(args),
                         {
                             'account_id': [self.client.account_id],
                         })

    def test_set_business_billing_edition(self):
        """Test to set PLATFORM billing edition
        """
        response = self.client.set_edition('PLATFORM')
        uri = response['uri']

        self.assertEqual(response['method'], 'POST')
        self.assertEqual(uri, '/admin/v1/billing/edition')
        self.assertEqual(json.loads(response['body']),
                         {
                             'edition': 'PLATFORM',
                             'account_id': self.client.account_id,
                         })

    def test_set_enterprise_billing_edition(self):
        """Test to set ENTERPRISE billing edition
        """
        response = self.client.set_edition('ENTERPRISE')
        uri = response['uri']

        self.assertEqual(response['method'], 'POST')
        self.assertEqual(uri, '/admin/v1/billing/edition')
        self.assertEqual(json.loads(response['body']),
                         {
                             'edition': 'ENTERPRISE',
                             'account_id': self.client.account_id,
                         })

    def test_get_telephony_credits(self):
        """Test to get telephony credits
        """
        response = self.client.get_telephony_credits()
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'GET')
        self.assertEqual(uri, '/admin/v1/billing/telephony_credits')
        self.assertEqual(util.params_to_dict(args),
                         {
                             'account_id': [self.client.account_id],
                         })

    def test_set_telephony_credits(self):
        """Test to set telephony credits
        """
        response = self.client.set_telephony_credits(10)
        uri = response['uri']

        self.assertEqual(response['method'], 'POST')
        self.assertEqual(uri, '/admin/v1/billing/telephony_credits')
        self.assertEqual(json.loads(response['body']),
                         {
                             'credits': '10',
                             'account_id': self.client.account_id,
                         })
