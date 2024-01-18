"""
Example of Duo Accounts API get child account edition
"""

import duo_client
import getpass

DUO_EDITIONS = {
        "ENTERPRISE": "Duo Essentials",
        "PLATFORM": "Duo Advantage",
        "BEYOND": "Duo Premier",
        "PERSONAL": "Duo Free"
}

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

    return {
            "ikey": ikey,
            "skey": skey,
            "host": host,
            "account_id": account_id,
    }


def main():
    """Main program entry point"""

    inputs = prompt_for_credentials()

    account_admin_api = duo_client.admin.AccountAdmin(**inputs)

    print(f"Getting edition for account ID {inputs['account_id']}...")
    result = account_admin_api.get_edition()
    if 'edition' not in result:
        print(f"An error occurred while getting edition for account {inputs['account_id']}")
        print(f"Error message: {result}")
    else:
        print(f"The current Duo Edition for account {inputs['account_id']} is '{result['edition']}' " +
              f"[{DUO_EDITIONS[result['edition']]}]")


if __name__ == '__main__':
    main()
