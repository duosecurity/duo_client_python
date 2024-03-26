"""
Example of Duo Accounts API child account deletiom
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
    account_id = _get_next_arg('ID of child account to delete: ')

    return {"IKEY": ikey, "SKEY": skey, "APIHOST": host, "ACCOUNT_ID": account_id}


def main():
    """Main program entry point"""

    inputs = prompt_for_credentials()

    account_client = duo_client.Accounts(
            ikey=inputs['IKEY'],
            skey=inputs['SKEY'],
            host=inputs['APIHOST']
    )

    account_name = None
    child_account_list = account_client.get_child_accounts()
    for account in child_account_list:
        if account['account_id'] == inputs['ACCOUNT_ID']:
            account_name = account['name']
    if account_name is None:
        print(f"Unable to find account with ID [{inputs['ACCOUNT_ID']}]")
        sys.exit()

    print(f"Deleting child account with name [{account_name}]")
    deleted_account = account_client.delete_account(inputs['ACCOUNT_ID'])
    if deleted_account == '':
        print(f"Account {inputs['ACCOUNT_ID']} was deleted successfully.")
    else:
        print(f"An unexpected error occurred while deleting account [{account_name}: {deleted_account}]")


if __name__ == '__main__':
    main()
