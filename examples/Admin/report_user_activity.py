#!/usr/bin/env python
import sys
from datetime import datetime, timezone

import duo_client

argv_iter = iter(sys.argv[1:])


def get_next_input(prompt):
    """Collect user input from terminal and return it."""
    try:
        return next(argv_iter)
    except StopIteration:
        return input(prompt)


def human_time(time: int) -> str:
    """Translate unix time into human readable string"""
    if time is None:
        date_str = 'Never'
    else:
        date_str = datetime.fromtimestamp(time, timezone.utc).strftime("%Y-%m-%m %H:%M:%S")
    return date_str


# Configuration and information about objects to create.
admin_api = duo_client.Admin(
        ikey=get_next_input('Admin API integration key ("DI..."): '),
        skey=get_next_input('integration secret key: '),
        host=get_next_input('API hostname ("api-....duosecurity.com"): '), )

# Retrieve user info from API:
users = admin_api.get_users()

print(f'{"Username":^30} {"Last Login":^20} {"User Enrolled"}')
print(f'{"=" * 30} {"=" * 20} {"=" * 15}')
for user in users:
    line_out = f"{user['username']:30} "
    line_out += f"{human_time(user['last_login']):20} "
    line_out += f" {user['is_enrolled']} "
    print(line_out)
