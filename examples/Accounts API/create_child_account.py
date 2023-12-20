"""
Example of Duo Accounts API child account creation
"""

import duo_client
import getpass


def _get_user_input(prompt, secure=False):
    """Read information from STDIN, using getpass when sensitive information should not be echoed to tty"""
    if secure is True:
        return getpass.getpass(prompt)
    else:
        return input(prompt)


def prompt_for_credentials() -> dict:
    """Collect required API credentials from command line prompts"""

    ikey = _get_user_input('Duo Accounts API integration key ("DI..."): ')
    skey = _get_user_input('Duo Accounts API integration secret key: ', secure=True)
    host = _get_user_input('Duo Accounts API hostname ("api-....duosecurity.com"): ')
    account_name = _get_user_input('Name for new child account: ')

    return {"IKEY": ikey, "SKEY": skey, "APIHOST": host, "ACCOUNT_NAME": account_name}


def main():
    """Main program entry point"""

    inputs = prompt_for_credentials()

    account_client = duo_client.Accounts(
            ikey=inputs['IKEY'],
            skey=inputs['SKEY'],
            host=inputs['APIHOST']
    )

    print(f"Creating child account with worker_name [{inputs['ACCOUNT_NAME']}]")
    child_account = account_client.create_account(inputs['ACCOUNT_NAME'])

    if 'account_id' in child_account:
        print(f"Child account for [{inputs['ACCOUNT_NAME']}] created successfully.")
        set_edition_result = account_client.e
    else:
        print(f"An unexpected error occurred while creating child account for {inputs['ACCOUNT_NAME']}")
    print(child_account)


if __name__ == '__main__':
    main()
