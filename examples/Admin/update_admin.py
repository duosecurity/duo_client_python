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

ADMIN_ID = get_next_arg('Admin Id: ')
NAME = get_next_arg('Admin name: ') or None
PHONE = get_next_arg('Phone number (e.g. 2154567890): ') or None
PASSWORD_CHANGE_REQ = get_next_arg('password_change_required: ') or None
STATUS = get_next_arg('status: ') or None
ROLE = get_next_arg('Administrative Role(Optional): ') or None
SUBACCOUNT_ROLE = get_next_arg('Subaccount Role(Optional): ') or None

updated_admin = admin_api.update_admin(admin_id=ADMIN_ID, 
                                       name=NAME, 
                                       phone=PHONE, 
                                       password_change_required=PASSWORD_CHANGE_REQ, 
                                       status=STATUS, 
                                       role=ROLE, 
                                       subaccount_role=SUBACCOUNT_ROLE)
print('Updated Admin: ')
pprint.pprint(updated_admin)
