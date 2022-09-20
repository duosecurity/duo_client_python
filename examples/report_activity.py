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
    ikey="DIRDJHGRLETC0XHV6W4F",
    skey="",
    host="api-dataeng.trustedpath.info",
)

# Retrieve user info from API:
mintime = '1659380517000'
maxtime = '1663700517000'
logs = admin_api.get_activity_logs(mintime = mintime, maxtime = maxtime)
print(logs)
