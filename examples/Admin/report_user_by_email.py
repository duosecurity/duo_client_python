#!/usr/bin/env python

""" Script to illustrate how to retrieve a user from the Duo Admin API using the associated email address"""

import sys
import getpass

import duo_client

argv_iter = iter(sys.argv[1:])


def get_next_arg(prompt, secure=False):
    """Read information from STDIN, using getpass when sensitive information should not be echoed to tty"""
    try:
        return next(argv_iter)
    except StopIteration:
        if secure is True:
            return getpass.getpass(prompt)
        else:
            return input(prompt)


def main():
    """ Primary script execution code """
    # Configuration and information about objects to create.
    admin_api = duo_client.Admin(
            ikey=get_next_arg('Admin API integration key ("DI..."): '),
            skey=get_next_arg('integration secret key: ', secure=True),
            host=get_next_arg('API hostname ("api-....duosecurity.com"): '),
    )

    # Retrieve user info from API:
    email_address = get_next_arg('E-mail address of user to retrieve: ')
    user = admin_api.get_user_by_email(email_address)

    if user:
        print(user)
    else:
        print(f"User with email [{email_address}] could not be found.")


if __name__ == '__main__':
    main()
