#!/usr/bin/env python
"""Print Duo Trust Monitor Events which surfaced within the past two weeks."""

from __future__ import print_function
from __future__ import absolute_import
import datetime
import json
import sys

from duo_client import Admin
from six.moves import input


argv_iter = iter(sys.argv[1:])
def get_next_arg(prompt):
    try:
        return next(argv_iter)
    except StopIteration:
        return input(prompt)


def main(args):
    # Instantiate the Admin client object.
    admin_client = Admin(args[0], args[1], args[2])

    # Query for Duo Trust Monitor events that were surfaced within the last two weeks (from today).
    now = datetime.datetime.utcnow()
    mintime_ms = int((now - datetime.timedelta(weeks=2)).timestamp() * 1000)
    maxtime_ms = int(now.timestamp() * 1000)

    # Loop over the returned iterator to navigate through each event, printing it to stdout.
    for event in admin_client.get_trust_monitor_events_iterator(mintime_ms, maxtime_ms):
        print(json.dumps(event, sort_keys=True))


def parse_args():
    ikey=get_next_arg('Duo Admin API integration key ("DI..."): ')
    skey=get_next_arg('Duo Admin API integration secret key: ')
    host=get_next_arg('Duo Admin API hostname ("api-....duosecurity.com"): ')
    return (ikey, skey, host,)


if __name__ == "__main__":
    args = parse_args()
    main(args)
