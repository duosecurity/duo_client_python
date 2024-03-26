"""
Example of Duo account API uaer accountentication with synchronous request/response
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

    return {"IKEY": ikey, "SKEY": skey, "APIHOST": host}


def main():
    """Main program entry point"""

    inputs = prompt_for_credentials()

    account_client = duo_client.Accounts(
            ikey=inputs['IKEY'],
            skey=inputs['SKEY'],
            host=inputs['APIHOST']
    )

    child_accounts = account_client.get_child_accounts()

    if isinstance(child_accounts, list):
        # Expected list of child accounts returned
        for child_account in child_accounts:
            print(child_account)

    if isinstance(child_accounts, dict):
        # Non-successful response returned
        print(child_accounts)


if __name__ == '__main__':
    main()
