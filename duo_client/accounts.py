"""
Duo Security Accounts API reference client implementation.

<http://www.duosecurity.com/docs/accountsapi>
"""
from __future__ import absolute_import
from . import client

class Accounts(client.Client):
    def get_child_accounts(self):
        """
        Return a list of all child accounts of the integration's account.
        """
        params = {}
        response = self.json_api_call('POST',
                                      '/accounts/v1/account/list',
                                      params)
        return response

    def create_account(self, name):
        """
        Create a new child account of the integration's account.
        """
        params = {
            'name': name,
        }
        response = self.json_api_call('POST',
                                      '/accounts/v1/account/create',
                                      params)
        return response

    def delete_account(self, account_id):
        """
        Delete a child account of the integration's account.
        """
        params = {
            'account_id': account_id,
        }
        response = self.json_api_call('POST',
                                      '/accounts/v1/account/delete',
                                      params)
        return response
