#!/usr/bin/env python
from __future__ import print_function
from __future__ import absolute_import
import csv
import sys
import duo_client
import json
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

# Retrieve log info from API:
logs = admin_api.get_authentication_log()

# Count authentications by country:
counts = dict()
for log in logs:
    country = log['location']['country']
    if country != '':
        counts[country] = counts.get(country, 0) + 1

# Print CSV of country, auth count:
auths_descending = sorted(counts.items(), reverse=True)
reporter = csv.writer(sys.stdout)
print("[+] Report of auth counts by country:")
reporter.writerow(('Country', 'Auth Count'))
for row in auths_descending:
    reporter.writerow([
        row[0],
        row[1],
    ])
