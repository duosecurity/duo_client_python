"""
Example of how to extract users and their aliases for a specific group from the Duo Admin API
"""

import sys
import argparse
import dataclasses
from collections import deque
from duo_client import Admin

DUO_MAX_USERS_PER_API_CALL = 100


@dataclasses.dataclass
class DuoUser:
    """
    Duo User object class for storage and retrieval of pertinent information per user
    """
    username: str = None
    user_id: str = None
    group_name: str = None
    aliases: str = None

    def set_group_name(self, group_name):
        self.group_name = group_name

    def set_aliases(self, aliases: list):
        self.aliases = ','.join(aliases)

    def get_user_info(self):
        return_string = (f"'username': {self.username}, 'user_id': {self.user_id}, " +
                         f"'group_name': {self.group_name}, 'aliases': '{self.aliases}'")
        return return_string


parser = argparse.ArgumentParser()
duo_arg_group = parser.add_argument_group('Duo Admin API Credentials')
duo_arg_group.add_argument('--ikey',
                           help='Duo Admin API IKEY',
                           required=True
                           )
duo_arg_group.add_argument('--skey',
                           help='Duo Admin API Secret Key',
                           required=True,
                           )
duo_arg_group.add_argument('--host',
                           help='Duo Admin API apihost',
                           required=True
                           )
parser.add_argument('--group_name',
                    help="Name of group to get users from. Groups are case-sensitive.",
                    required=True
                    )
args = parser.parse_args()

duo_admin_client = Admin(
        ikey=args.ikey,
        skey=args.skey,
        host=args.host
)


def split_list(input_list: list, size: int) -> list:
    """Split a list into chunks based on size"""
    return [input_list[i:i + size] for i in range(0, len(input_list), size)]


def get_duo_group_users(group_name: str) -> list:
    """Get the list of users assigned to the given group name"""
    group_id = None
    try:
        groups = (duo_admin_client.get_groups())
    except Exception as e_str:
        print(f"Exception while retrieving groups: {e_str}")
        sys.exit(1)

    for group in groups:
        if group['name'] == group_name:
            group_id = group['group_id']
            break

    user_list = list(deque(duo_admin_client.get_group_users_iterator(group_id)))
    return split_list(user_list, DUO_MAX_USERS_PER_API_CALL)


def get_duo_user_aliases(user_list: list[list]) -> list:
    """Collect aliases for the users in the given list"""
    all_users = []
    for u_list in user_list:
        users = list(deque(duo_admin_client.get_users_by_ids([uid['user_id'] for uid in u_list])))
        for user in users:
            new_duo_user = DuoUser(user_id=user['user_id'], username=user['username'])
            new_duo_user.set_aliases(list(user['aliases'].values()))
            all_users.append(new_duo_user)
    return all_users


def output_user_aliases(user_list: list[DuoUser], group_name: str) -> None:
    """Output the list of users and their aliases for the requested group"""
    for user in user_list:
        user.set_group_name(group_name)
        print(user.get_user_info())


def main():
    """Main program entry point"""
    if args.group_name is not None:
        duo_group_users = get_duo_group_users(args.group_name)
        if len(duo_group_users) == 0:
            print(f"Unable to find users assigned to group named '{args.group_name}'.")
            sys.exit(1)
        duo_group_user_aliases = get_duo_user_aliases(duo_group_users)
        output_user_aliases(duo_group_user_aliases, args.group_name)


if __name__ == '__main__':
    main()
