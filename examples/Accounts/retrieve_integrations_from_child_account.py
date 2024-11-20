"""
Example of creating an integration in a child account using parent account credentials
"""

import argparse
import duo_client


parser = argparse.ArgumentParser()
duo_arg_group = parser.add_argument_group('Duo Accounts API Credentials')
duo_arg_group.add_argument('--ikey',
                           help='Duo Accounts API IKEY',
                           required=True
                           )
duo_arg_group.add_argument('--skey',
                           help='Duo Accounts API Secret Key',
                           required=True,
                           )
duo_arg_group.add_argument('--host',
                           help='Duo child account API apihost',
                           required=True
                           )
parser.add_argument('--child_account_id',
                    help='The Duo account ID of the child account to query.',
                    required=True
                    )
args = parser.parse_args()

# It is important to note that we are using the IKEY/SKEY combination for an Accounts API integration in the
# parent account along with the api-hostname of a child account to create a new duo_client.Admin instance
account_client = duo_client.Admin(
        ikey=args.ikey,
        skey=args.skey,
        host=args.host,
)

# Once the duo_client.Admin instance is created, the child account_id is assigned. This is necessary to ensure
# queries made with this Admin API instance are directed to the proper child account that matches the api-hostname
# used to create the instance.
account_client.account_id = args.child_account_id


def main():
    """Main program entry point"""

    print(f"Retrieving integrations for child account {args.child_account_id}")
    child_account_integrations = account_client.get_integrations_generator()
    for integration in child_account_integrations:
        print(f"{integration['name']=}")


if __name__ == '__main__':
    main()
