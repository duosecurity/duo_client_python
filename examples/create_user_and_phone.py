#!/usr/bin/python
import pprint
import sys

import duo_client

argv_iter = iter(sys.argv[1:])
def get_next_arg(prompt):
    try:
        return argv_iter.next()
    except StopIteration:
        return raw_input(prompt)

# Configuration and information about objects to create.
ADMIN_API_CFG = {
    'ikey': get_next_arg('ikey ("DI..."): '),
    'skey': get_next_arg('integration secret key: '),
    'host': get_next_arg('API hostname ("api-....duosecurity.com"): '),
}

USERNAME = get_next_arg('user login name: ')
REALNAME = get_next_arg('user full name: ')

# Refer to http://www.duosecurity.com/docs/adminapi for more
# information about phone types and platforms.
PHONE_NUMBER = get_next_arg('phone number (e.g. +1-555-123-4567): ')
PHONE_TYPE = get_next_arg('phone type (e.g. mobile): ')
PHONE_PLATFORM = get_next_arg('phone platform (e.g. google android): ')

# Create and return a new user object.
user = duo_client.admin.add_user(
    username=USERNAME,
    realname=REALNAME,
    **ADMIN_API_CFG
)
print 'Created user:'
pprint.pprint(user)

# Create and return a new phone object.
phone = duo_client.admin.add_phone(
    number=PHONE_NUMBER,
    type=PHONE_TYPE,
    platform=PHONE_PLATFORM,
    **ADMIN_API_CFG
)
print 'Created phone:'
pprint.pprint(phone)

# Associate the user with the phone.
duo_client.admin.add_user_phone(
    user_id=user['user_id'],
    phone_id=phone['phone_id'],
    **ADMIN_API_CFG
)
print 'Added phone', phone['number'], 'to user', user['username']

# Send two SMS messages to the phone with information about installing
# the app for PHONE_PLATFORM and activating it with this Duo account.
act_sent = duo_client.admin.send_sms_activation_to_phone(
    phone_id=phone['phone_id'],
    install='1',
    **ADMIN_API_CFG
)
print 'SMS activation sent to', phone['number'] + ':'
pprint.pprint(act_sent)
