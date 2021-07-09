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

# Local
# admin_api = duo_client.Admin(
#     ikey='DIRN4GZCBZPD9XLONH05',
#     skey='a3mvONCaAzZXehm6getAgN7PNBCtQ8ENM6O6iqZm',
#     host='api-duo1.duo.test',
# )

# First- jcheng's best account
admin_api = duo_client.Admin(
    ikey='DI1J86WQ29P4T8F4R3UO',
    skey='vNiMlXDytkBA6w658ejsHLBkAH7h3FaVcJbcsmkT',
    host='api-db9c06d6.test.duosecurity.com',
)

# res = admin_api.json_api_call('GET', '/admin/v1/settings', {})

res = admin_api.update_settings(
    helpdesk_can_send_enroll_email=True,
    helpdesk_bypass_expiration=120)


import pprint

pp = pprint.PrettyPrinter(indent=4)
pp.pprint(res)
