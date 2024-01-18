"""
Example of Duo Accounts API set child account edition
"""

import duo_client
import getpass

ALLOWED_DUO_EDITIONS = ("PERSONAL", "ENTERPRISE", "PLATFORM", "BEYOND")

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
    account_id = _get_user_input('Child account ID: ')
    account_apihost = _get_user_input('Child account api_hostname: ')
    account_edition = _get_user_input('Child account edition: ')
    while account_edition.upper() not in ALLOWED_DUO_EDITIONS:
        print(f"Invalid account edition. Please select one of {ALLOWED_DUO_EDITIONS}")
        account_edition = _get_user_input('Child account edition: ')

    return {
            "ikey": ikey,
            "skey": skey,
            "host": host,
            "account_id": account_id,
            "child_api_host": account_apihost,
            "account_edition": account_edition,
    }


def main():
    """Main program entry point"""

    inputs = prompt_for_credentials()
    edition = inputs.pop('account_edition')
    edition = edition.upper()

    account_admin_api = duo_client.admin.AccountAdmin(**inputs)

    print(f"Setting edition for account ID {inputs['account_id']} to {edition}")
    result = account_admin_api.set_edition(edition)
    if result != "":
        print(f"An error occurred while setting edition for account {inputs['account_id']}")
        print(f"Error message: {result}")
    else:
        print(f"Edition [{edition}] successfully set for account ID {inputs['account_id']}")


if __name__ == '__main__':
    main()
