"""
Duo Security Admin API subaccount management reference client implementation.

<https://duo.com/docs/adminapi#subaccounts>

DEPRECATED: this module is deprecated and will be removed in a future release.
Use the equivalent methods on duo_client.Admin instead.
"""
from . import client

class Accounts(client.Client):
    """
    DEPRECATED: use duo_client.Admin instead. This client will be removed in a
    future release.

    The subaccount methods below are duplicated on Admin and are frozen: they
    will not be updated going forward. Any new subaccount API method is added
    to Admin only, and fixes to these methods may not be mirrored here.
    """
    child_map = {}

    def get_child_accounts(self):
        """
        Return a list of all child accounts of the integration's account.

        DEPRECATED: use Admin.get_child_accounts instead. Not maintained.
        """
        params = {}
        response = self.json_api_call('POST',
                                      '/accounts/v1/account/list',
                                      params)
        if response and isinstance(response, list):
            for account in response:
                account_id = account.get('account_id', None)
                api_hostname = account.get('api_hostname', None)
                if account_id and api_hostname:
                    Accounts.child_map[account_id] = api_hostname
        return response

    def create_account(self, name):
        """
        Create a new child account of the integration's account.

        DEPRECATED: use Admin.create_account instead. Not maintained.
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

        DEPRECATED: use Admin.delete_account instead. Not maintained.
        """
        params = {
            'account_id': account_id,
        }
        response = self.json_api_call('POST',
                                      '/accounts/v1/account/delete',
                                      params)
        return response
