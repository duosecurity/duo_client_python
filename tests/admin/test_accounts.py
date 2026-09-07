import json

import duo_client.admin
from .. import util
from .base import TestAdmin


class TestAccounts(TestAdmin):
    def test_get_child_accounts(self):
        """ Test to get child accounts.
        """
        response = self.client_list.get_child_accounts()
        response = response[0]
        self.assertEqual(response['method'], 'POST')
        self.assertEqual(response['uri'], '/accounts/v1/account/list')
        self.assertEqual(
            json.loads(response['body']),
            {
                'account_id': self.client.account_id,
            })

    def test_create_account(self):
        """ Test to create a child account.
        """
        response = self.client.create_account('Test Account')
        self.assertEqual(response['method'], 'POST')
        self.assertEqual(response['uri'], '/accounts/v1/account/create')
        self.assertEqual(
            json.loads(response['body']),
            {
                'name': 'Test Account',
                'account_id': self.client.account_id,
            })

    def test_delete_account(self):
        """ Test to delete a child account.
        """
        client = duo_client.admin.Admin('test_ikey', 'test_akey', 'example.com')
        client._connect = lambda: util.MockHTTPConnection()

        response = client.delete_account('DA099999999999999999')
        self.assertEqual(response['method'], 'POST')
        self.assertEqual(response['uri'], '/accounts/v1/account/delete')
        self.assertEqual(
            json.loads(response['body']),
            {
                'account_id': 'DA099999999999999999',
            })

    def test_delete_account_when_client_is_account_scoped(self):
        """ Test that a client-level account_id overrides the delete target.

        Admin.api_call sets params['account_id'] from self.account_id, so an
        account-scoped client cannot delete a different account.
        """
        response = self.client.delete_account('DA099999999999999999')
        self.assertEqual(
            json.loads(response['body']),
            {
                'account_id': self.client.account_id,
            })
