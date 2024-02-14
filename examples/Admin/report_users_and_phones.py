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

# Configuration and information about objects to create.
admin_api = duo_client.Admin(
    ikey=get_next_arg('Admin API integration key ("DI..."): '),
    skey=get_next_arg('integration secret key: '),
    host=get_next_arg('API hostname ("api-....duosecurity.com"): '),
)

# Retrieve user info from API:
users = admin_api.get_users()

# Print CSV of username, phone number, phone type, and phone platform:
#
# (If a user has multiple phones, there will be one line printed per
# associated phone.)
reporter = csv.writer(sys.stdout)
print("[+] Report of all users and associated phones:")
reporter.writerow(('Username', 'Phone Number', 'Type', 'Platform'))
for user in users:
    for phone in user["phones"]:
        reporter.writerow([
                user["username"],
                phone["number"],
                phone["type"],
                phone["platform"],
        ])
