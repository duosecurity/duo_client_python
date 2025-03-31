#!/usr/bin/python
import pprint
import sys

import duo_client

argv_iter = iter(sys.argv[1:])
def get_next_arg(prompt):
    try:
        return next(argv_iter)
    except StopIteration:
        return input(prompt)
    
# Configuration and information about objects to create.
admin_api = duo_client.Admin(
    ikey=get_next_arg('Admin API integration key ("DI..."): '),
    skey=get_next_arg('integration secret key: '),
    host=get_next_arg('API hostname ("api-....duosecurity.com"): '),
)

NAME = get_next_arg('Admin name: ')
EMAIL = get_next_arg('Email: ')
PHONE = get_next_arg('Phone number (e.g. 2154567890): ')
PASSWORD = get_next_arg('Password: ')
ROLE = get_next_arg('Administrative Role(Optional): ') or None
SUBACCOUNT_ROLE = get_next_arg('Subaccount Role(Optional): ') or None

created_admin = admin_api.add_admin(NAME, EMAIL, PHONE, PASSWORD, ROLE, SUBACCOUNT_ROLE)
print('Created Admin: ')
pprint.pprint(created_admin)
