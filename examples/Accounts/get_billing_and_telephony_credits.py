#!/usr/bin/env python
import sys

import duo_client

EDITIONS = {
        "ENTERPRISE": "Duo Essentials",
        "PLATFORM": "Duo Advantage",
        "BEYOND": "Duo Premier",
        "PERSONAL": "Duo Free"
}

def get_next_input(prompt):
    try:
        return next(iter(sys.argv[1:]))
    except StopIteration:
        return input(prompt)


def main():
    """Program entry point"""
    ikey=get_next_input('Accounts API integration key ("DI..."): ')
    skey=get_next_input('Accounts API integration secret key: ')
    host=get_next_input('Accounts API hostname ("api-....duosecurity.com"): ')

    # Configuration and information about objects to create.
    accounts_api = duo_client.Accounts(
        ikey=ikey,
        skey=skey,
        host=host,
    )

    kwargs = {
            'ikey': ikey,
            'skey': skey,
            'host': host,
    }

    # Get all child accounts
    child_accounts = accounts_api.get_child_accounts()

    for child_account in child_accounts:
        # Create AccountAdmin with child account_id, child api_hostname and kwargs consisting of ikey, skey, and host
        account_admin_api = duo_client.admin.AccountAdmin(
                child_account['account_id'],
                child_api_host = child_account['api_hostname'],
                **kwargs,
        )
        try:
            # Get edition of child account
            child_account_edition = account_admin_api.get_edition()
            print(f"Edition for child account {child_account['name']}: {child_account_edition['edition']}")
        except RuntimeError as err:
            # The account might not have access to get billing information
            if "Received 403 Access forbidden" == str(err):
                print("{error}: No access for billing feature".format(error=err))
            else:
                print(err)

        try:
            # Get telephony credits of child account
            child_telephony_credits = account_admin_api.get_telephony_credits()
            print("Telephony credits for child account {name}: {edition}".format(
                name=child_account['name'],
                edition=child_telephony_credits['credits'])
            )
        except RuntimeError as err:
            # The account might not have access to get telephony credits
            if "Received 403 Access forbidden" == str(err):
                print("{error}: No access for telephony feature".format(error=err))
            else:
                print(err)


if __name__ == "__main__":
    main()
