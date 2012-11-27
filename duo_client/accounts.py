"""
Duo Security Accounts API reference client implementation.

<http://www.duosecurity.com/docs/accountsapi>
"""
import urllib

import client

def get_child_accounts(ikey, skey, host, ca=None):
    """
    Return a list of all child accounts of the integration's account.
    """
    response = client.call_json_api(ikey, skey, host,
                                    'POST',
                                    '/accounts/v1/account/list',
                                    ca=ca)
    return response

def create_account(ikey, skey, host, name, ca=None):
    """
    Create a new child account of the integration's account.
    """
    response = client.call_json_api(ikey, skey, host,
                                    'POST',
                                    '/accounts/v1/account/create',
                                    name=name,
                                    ca=ca)
    return response

def delete_account(ikey, skey, host, account_id, ca=None):
    """
    Delete a child account of the integration's account.
    """
    response = client.call_json_api(ikey, skey, host,
                                    'POST',
                                    '/accounts/v1/account/delete',
                                    account_id=account_id,
                                    ca=ca)
    return response
