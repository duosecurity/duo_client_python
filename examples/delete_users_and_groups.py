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

# Configuration and information about objects to create.
admin_api = duo_client.Admin(
    ikey=get_next_arg('Admin API integration key ("DI..."): '),
    skey=get_next_arg('integration secret key: '),
    host=get_next_arg('API hostname ("api-....duosecurity.com"): '),
)

[ admin_api.delete_user(r['user_id']) for r in admin_api.get_users() ]
[ admin_api.delete_group(r['group_id']) for r in admin_api.get_groups() ]

