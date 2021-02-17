#!/usr/bin/env python
from __future__ import absolute_import
from __future__ import print_function
import csv
import sys

import duo_client
from six.moves import input

argv_iter = iter(sys.argv[1:])
def get_next_arg(prompt):
    try:
        return next(argv_iter)
    except StopIteration:
        return input(prompt)

ikey=get_next_arg('Accounts API integration key ("DI..."): ')
skey=get_next_arg('Accounts API integration secret key: ')
host=get_next_arg('Accounts API hostname ("api-....duosecurity.com"): ')

# Configuration and information about objects to create.
accounts_api = duo_client.Accounts(
    ikey=ikey,
    skey=skey,
    host=host,
)

kwargs = {
        'ikey': ikey,
        'skey': skey,
        'host': host,
}

# Get all child accounts
child_accounts = accounts_api.get_child_accounts()

for child_account in child_accounts:
    # Create AccountAdmin with child account_id and kwargs consisting of ikey, skey, and host
    account_admin_api = duo_client.admin.AccountAdmin(
            child_account['account_id'],
            **kwargs,
    )
    try:
        # Get edition of child account
        child_account_edition = account_admin_api.get_edition()
        print("Edition for child account {name}: {edition}".format(
            name=child_account['name'],
            edition=child_account_edition['edition'])
        )
    except RuntimeError as err:
        # The account might not have access to get billing information
        if "Received 403 Access forbidden" == str(err):
            print("{error}: No access for billing feature".format(error=err))
        else:
            print(err)

    try:
        # Get telephony credits of child account
        child_telephony_credits = account_admin_api.get_telephony_credits()
        print("Telephony credits for child account {name}: {edition}".format(
            name=child_account['name'],
            edition=child_telephony_credits['credits'])
        )
    except RuntimeError as err:
        # The account might not have access to get telephony credits 
        if "Received 403 Access forbidden" == str(err):
            print("{error}: No access for telephony feature".format(error=err))
        else:
            print(err)
