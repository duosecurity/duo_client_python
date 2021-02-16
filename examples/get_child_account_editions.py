#!/usr/bin/python
from __future__ import absolute_import
from __future__ import print_function
import pprint
import sys

import duo_client
from six.moves import input

argv_iter = iter(sys.argv[1:])
def get_next_arg(prompt):
    try:
        return next(argv_iter)
    except StopIteration:
        return input(prompt)

ikey=get_next_arg('MSP Accounts API integration key ("DI..."): ')
skey=get_next_arg('integration secret key: ')
host=get_next_arg('API hostname ("api-....duosecurity.com"): ')

# Configuration and information about objects to create.
accounts_api = duo_client.Accounts(
    ikey=ikey,
    skey=skey,
    host=host,
)

admin_api = duo_client.Admin(
    ikey=ikey,
    skey=skey,
    host=host,
)
# Gather all child accounts
account_list = accounts_api.get_child_accounts()

print('Child Accounts:')
pprint.pprint(account_list)

# Get Billing Edition for all child accounts
for acct in account_list:
  admin_api.account_id=acct['account_id']
  edition = admin_api.get_billing_edition()
  print('Child Account [{}] is using edition: {}'.format(acct['name'], edition['edition']))
