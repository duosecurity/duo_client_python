"""
Script to pull list of all phones and modify the name of each
"""

import sys
import getpass

import duo_client

argv_iter = iter(sys.argv[1:])


def _get_next_arg(prompt, secure=False):
    """Read information from STDIN, using getpass when sensitive information should not be echoed to tty"""
    try:
        return next(argv_iter)
    except StopIteration:
        if secure is True:
            return getpass.getpass(prompt)
        else:
            return input(prompt)


admin_api = duo_client.Admin(
        ikey=_get_next_arg('Admin API integration key ("DI..."): '),
        skey=_get_next_arg('integration secret key: ', secure=True),
        host=_get_next_arg('API hostname ("api-....duosecurity.com"): '),
)

phones = admin_api.get_phones()

for phone in phones:
    print(f"Current phone name for device ID {phone['phone_id']} is {phone['name']}")
    new_phone_name = phone['name'] + '_new'
    print(f"Changing name to {new_phone_name}")
    result = admin_api.update_phone(phone_id=phone['phone_id'], name=new_phone_name)
    if result['name'] == new_phone_name:
        print(f"Device {phone['phone_id']} is now named {new_phone_name}.")
    else:
        print("An error occurred.")

