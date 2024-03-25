"""
Example of creating an integration in a child account using parent account credentials

The key to successfully interacting with child accounts via the parent account APIs is
pairing the parent account API IKEY/SKEY combination with the api-host of the child account.
Once that connection is established, the child account ID must be passed along with all API interactions.
The duo_client SDK makes that easy by allowing the setting of the child account ID as an instance variable.
"""

import sys
import getpass
import duo_client

# Create an interator to be used by the interactive terminal prompt
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
    answers = {'ikey':       _get_next_arg('Duo Accounts API integration key ("DI..."): '),
               'skey':       _get_next_arg('Duo Accounts API integration secret key: ', secure=True),
               'host':       _get_next_arg('Duo API hostname of child account ("api-....duosecurity.com"): '),
               'account_id': _get_next_arg('Child account ID: '), 
               'app_name': _get_next_arg('New application name: '),
               'app_type':   _get_next_arg('New application type: ')}
    return answers


def create_child_integration(inputs: dict):
    """Create new application integration in child account via the parent account API"""

    # First create a duo_client.Admin instance using the parent account ikey/sky along with the child account api-host
    account_client = duo_client.Admin(ikey=inputs['ikey'], skey=inputs['skey'], host=inputs['host'])
    # Next assign the child account ID to the duo_client.Admin instance variable.
    account_client.account_id = inputs['account_id']
    # Now all API calls made via this instance will contain all of the minimum requirements to interact with the
    # child account.

    # Here only the two required arguments (name and type) are passed.
    # Normally, much more information would be provided. The type of additional information
    # varies by the type of application integration.
    try:
        new_app = account_client.create_integration(
                name=inputs['app_name'],
                integration_type=inputs['app_type'],
        )
        print(f"New application {inputs['app_name']} (ID: {new_app['integration_key']}) was created successfully.")
    except RuntimeError as e_str:
        # Any failure of the API call results in a generic Runtime Error
        print(f"An error occurred while creating the new application: {e_str}")


def main():
    """Main program entry point"""
    inputs = prompt_for_credentials()
    create_child_integration(inputs)


if __name__ == '__main__':
    main()
