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

USERNAME = get_next_arg('user login name: ')
REALNAME = get_next_arg('user full name: ')

# Refer to http://www.duosecurity.com/docs/adminapi for more
# information about phone types and platforms.
PHONE_NUMBER = get_next_arg('phone number (e.g. +1-555-123-4567): ')
PHONE_TYPE = get_next_arg('phone type (e.g. mobile): ')
PHONE_PLATFORM = get_next_arg('phone platform (e.g. google android): ')

# Create and return a new user object.
user = admin_api.add_user(
    username=USERNAME,
    realname=REALNAME,
)
print('Created user:')
pprint.pprint(user)

# Create and return a new phone object.
phone = admin_api.add_phone(
    number=PHONE_NUMBER,
    type=PHONE_TYPE,
    platform=PHONE_PLATFORM,
)
print('Created phone:')
pprint.pprint(phone)

# Associate the user with the phone.
admin_api.add_user_phone(
    user_id=user['user_id'],
    phone_id=phone['phone_id'],
)
print('Added phone', phone['number'], 'to user', user['username'])

# Send two SMS messages to the phone with information about installing
# the app for PHONE_PLATFORM and activating it with this Duo account.
act_sent = admin_api.send_sms_activation_to_phone(
    phone_id=phone['phone_id'],
    install='1',
)
print('SMS activation sent to', phone['number'] + ':')
pprint.pprint(act_sent)
