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

limit_of_apps=get_next_arg('Numerical limit of integrations to collect: ')

# Retrieve limited number of integrations from API:
integrations = admin_api.get_integrations(limit_of_apps)
print(integrations)
# Print CSV of integration name and ikey:
#
# 
## use the following below once line 27 above works properly
#reporter = csv.writer(sys.stdout)
#print("[+] Report of all integrations:")
#reporter.writerow(('integration_key', 'name'))
#for app in integrations:
#  reporter.writerow([
#    app["name"],
#    app["integration_key"],
#  ])