"""
Example of Duo Admin API policies operations
"""
import json
import duo_client
from getpass import getpass


class DuoPolicy():
    """Base class for Duo Policy object properties and methods"""

    def __init__(self):
        """Initialize Duo Policy"""
        ...


def get_next_user_input(prompt: str, secure: bool = False) -> str:
    """Collect input from user via standard input device"""
    return getpass(prompt) if secure is True else input(prompt)


admin_api = duo_client.Admin(
        ikey=get_next_user_input('Admin API integration key ("DI..."): '),
        skey=get_next_user_input("Admin API integration secret key: ", secure=True),
        host=get_next_user_input('API hostname ("api-....duosecurity.com"): '),
)


def create_empty_policy(name, print_response=False):
    """
    Create an empty policy with a specified name.
    """

    json_request = {
            "policy_name": name,
    }
    response = admin_api.create_policy_v2(json_request)
    if print_response:
        pretty = json.dumps(response, indent=4, sort_keys=True, default=str)
        print(pretty)
    return response.get("policy_key")


def create_policy_browsers(name, print_response=False):
    """
    Create a policy that blocks internet explorer browsers. Requires
    Access or Beyond editions.
    """

    json_request = {
            "policy_name": name,
            "sections":    {
                    "browsers": {
                            "blocked_browsers_list": [
                                    "ie",
                            ],
                    },
            },
    }
    response = admin_api.create_policy_v2(json_request)
    if print_response:
        pretty = json.dumps(response, indent=4, sort_keys=True, default=str)
        print(pretty)
    return response.get("policy_key")


def copy_policy(name1, name2, copy_from, print_response=False):
    """
    Copy the policy `copy_from` to two new policies.
    """
    response = admin_api.copy_policy_v2(copy_from, [name1, name2])
    if print_response:
        pretty = json.dumps(response, indent=4, sort_keys=True, default=str)
        print(pretty)
    policies = response.get("policies")
    return (policies[0].get("policy_key"), policies[1].get("policy_key"))


def bulk_delete_section(policy_keys, print_response=False):
    """
    Delete the section "browsers" from the provided policies.
    """
    response = admin_api.update_policies_v2("", ["browsers"], policy_keys)
    if print_response:
        pretty = json.dumps(response, indent=4, sort_keys=True, default=str)
        print(pretty)

def update_policy_with_device_health_app(policy_key, print_response=False):
    """
    Update a given policy to include Duo Device Health App policy
    settings. Requires Access or Beyond editions.
    NOTE: this function is deprecated, please use update_policy_with_duo_desktop
    """
    return update_policy_with_duo_desktop(policy_key, print_response)

def update_policy_with_duo_desktop(policy_key, print_response=False):
    """
    Update a given policy to include Duo Desktop policy
    settings. Requires Access or Beyond editions.
    """

    json_request = {
            "sections": {
                    "duo_desktop": {
                            "enforce_encryption":             ["windows"],
                            "enforce_firewall":               ["windows"],
                            "requires_duo_desktop":           ["windows"],
                            "windows_endpoint_security_list": ["cisco-amp"],
                            "windows_remediation_note":       "Please install Windows agent",
                    },
            },
    }
    response = admin_api.update_policy_v2(policy_key, json_request)
    if print_response:
        pretty = json.dumps(response, indent=4, sort_keys=True, default=str)
        print(pretty)
    return response.get("policy_key")


def get_policy(policy_key):
    """
    Fetch a given policy.
    """

    response = admin_api.get_policy_v2(policy_key)
    pretty = json.dumps(response, indent=4, sort_keys=True, default=str)
    print(pretty)


def iterate_all_policies():
    """
    Loop over each policy.
    """

    print("#####################")
    print("Iterating over all policies...")
    print("#####################")
    iter = sorted(
            admin_api.get_policies_v2_iterator(), key=lambda x: x.get("policy_name")
    )
    for policy in iter:
        print(
                "##################### {} {}".format(
                        policy.get("policy_name"), policy.get("policy_key")
                )
        )
        pretty = json.dumps(policy, indent=4, sort_keys=True, default=str)
        print(pretty)


def main():
    """Primary program entry point"""
    # Create two empty policies
    policy_key_a = create_empty_policy("Test New Policy - a")
    policy_key_b = create_empty_policy("Test New Policy - b")

    # Update policy with Duo Desktop settings.
    update_policy_with_duo_desktop(policy_key_b)

    # Create an empty policy and delete it.
    policy_key_c = create_empty_policy("Test New Policy - c")
    admin_api.delete_policy_v2(policy_key_c)

    # Create a policy with browser restriction settings.
    policy_key_d = create_policy_browsers("Test New Policy - d")

    # Copy a policy to 2 new policies.
    policy_key_e, policy_key_f = copy_policy("Test New Policy - e", "Test New Policy - f", policy_key_d)

    # Delete the browser restriction settings from 2 policies.
    bulk_delete_section([policy_key_e, policy_key_f])

    # Fetch the global and other custom policy.
    get_policy("global")
    get_policy(policy_key_b)

    # Loop over each policy.
    iterate_all_policies()


if __name__ == "__main__":
    main()
