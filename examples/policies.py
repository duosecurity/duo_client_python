#!/usr/bin/env python
import sys
import json
import duo_client
from six.moves import input


argv_iter = iter(sys.argv[1:])


def get_next_arg(prompt):
    try:
        return next(argv_iter)
    except StopIteration:
        return input(prompt)


admin_api = duo_client.Admin(
    ikey=get_next_arg('Admin API integration key ("DI..."): '),
    skey=get_next_arg("integration secret key: "),
    host=get_next_arg('API hostname ("api-....duosecurity.com"): '),
)


def create_empty_policy(name, print_response=False):
    """
    Create an empty policy with a specified name.
    """

    json_request = {
        "name": name,
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
        "name": name,
        "sections": {
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


def update_policy_with_device_health_app(policy_key, print_response=False):
    """
    Update a given policy to include Duo Device Health App policy
    settings. Requires Access or Beyond editions.
    """

    json_request = {
        "sections": {
            "device_health_app": {
                "enforce_encryption": ["windows"],
                "enforce_firewall": ["windows"],
                "prompt_to_install": ["windows"],
                "requires_DHA": ["windows"],
                "windows_endpoint_security_list": ["cisco-amp"],
                "windows_remediation_note": "Please install Windows agent",
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
    iter = sorted(admin_api.get_policies_v2_iterator(), key=lambda x: x.get("name"))
    for policy in iter:
        print(
            "##################### {} {}".format(
                policy.get("name"), policy.get("policy_key")
            )
        )
        pretty = json.dumps(policy, indent=4, sort_keys=True, default=str)
        print(pretty)


def main():
    # Create two empty policies
    policy_key_a = create_empty_policy("Test New Policy - a")
    policy_key_b = create_empty_policy("Test New Policy - b")

    # Update policy with Duo Device Health App settings.
    update_policy_with_device_health_app(policy_key_b)

    # Create an empty policy and delete it.
    policy_key_c = create_empty_policy("Test New Policy - c")
    admin_api.delete_policy_v2(policy_key_c)

    # Create a policy with browser restriction settings.
    policy_key_d = create_policy_browsers("Test New Policy - d")

    # Fetch the global and other custom policy.
    get_policy("global")
    get_policy(policy_key_b)

    # Loop over each policy.
    iterate_all_policies()


if __name__ == "__main__":
    main()
