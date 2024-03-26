"""
Example of Duo Accounts API child account creation
"""

import duo_client

import sys
import getpass

from pprint import pprint


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


def prompt_for_credentials() -> dict:
    """Collect required API credentials from command line prompts

    :return: dictionary containing Duo Accounts API ikey, skey and hostname strings
    """

    ikey = _get_next_arg('Duo Accounts API integration key ("DI..."): ')
    skey = _get_next_arg('Duo Accounts API integration secret key: ', secure=True)
    host = _get_next_arg('Duo Accounts API hostname ("api-....duosecurity.com"): ')
    account_name = _get_next_arg('Name for new child account: ')

    return {"IKEY": ikey, "SKEY": skey, "APIHOST": host, "ACCOUNT_NAME": account_name}


def main():
    """Main program entry point"""

    inputs = prompt_for_credentials()

    account_client = duo_client.Accounts(
            ikey=inputs['IKEY'],
            skey=inputs['SKEY'],
            host=inputs['APIHOST']
    )

    print(f"Creating child account with name [{inputs['ACCOUNT_NAME']}]")
    child_account = account_client.create_account(inputs['ACCOUNT_NAME'])

    if 'account_id' in child_account:
        print(f"Child account for [{inputs['ACCOUNT_NAME']}] created successfully.")
    else:
        print(f"An unexpected error occurred while creating child account for {inputs['ACCOUNT_NAME']}")
    print(child_account)


if __name__ == '__main__':
    main()
