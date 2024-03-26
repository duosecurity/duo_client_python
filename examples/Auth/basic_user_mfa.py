"""
Example of Duo Auth API uaer authentication with synchronous request/response
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

    :return: dictionary containing Duo Auth API ikey, skey and hostname strings
    """

    ikey = _get_next_arg('Duo Auth API integration key ("DI..."): ')
    skey = _get_next_arg('Duo Auth API integration secret key: ', secure=True)
    host = _get_next_arg('Duo Auth API hostname ("api-....duosecurity.com"): ')
    username = _get_next_arg('Duo Username: ')

    return {"USERNAME": username, "IKEY": ikey, "SKEY": skey, "APIHOST": host}


def main():
    """Main program entry point"""

    inputs = prompt_for_credentials()

    auth_client = duo_client.Auth(
            ikey=inputs['IKEY'],
            skey=inputs['SKEY'],
            host=inputs['APIHOST']
    )

    # Verify that the Duo service is available
    duo_ping = auth_client.ping()
    if 'time' in duo_ping:
        print("\nDuo service check completed successfully.")
    else:
        print(f"Error: {duo_ping}")

    # Verify that IKEY and SKEY information provided are valid
    duo_check= auth_client.check()
    if 'time' in duo_check:
        print("IKEY and SKEY provided have been verified.")
    else:
        print(f"Error: {duo_check}")

    # Execute pre-authentication for given user
    print(f"\nExecuting pre-authentication for {inputs['USERNAME']}...")
    pre_auth = auth_client.preauth(username=inputs['USERNAME'])

    if pre_auth['result'] == "auth":
        try:
            # User exists and has an MFA device enrolled
            print(f"Executing authentication action for {inputs['USERNAME']}...")
            # "auto" is selected for the factor in this example, however the pre_auth['devices'] dictionary
            # element contains a list of factors available for the provided user, if an alternate method is desired
            auth = auth_client.auth(factor="auto", username=inputs['USERNAME'], device="auto")
            print(f"\n{auth['status_msg']}")
        except Exception as e_str:
            print(e_str)
    elif pre_auth['result'] == "allow":
        # User is in bypass mode
        print(pre_auth['status_msg'])
    elif pre_auth['result'] == "enroll":
        # User is unknown and not enrolled in Duo with a 'New User' policy setting of 'Require Enrollment'
        # Setting a 'New User' policy to 'Require Enrollment' should only be done for Group level policies where
        # the intent is to capture "partially enrolled" users. "Parially enrolled" users are those that Duo has a
        # defined username but does not have an MFA device enrolled.
        print("Please enroll in Duo using the following URL.")
        print(pre_auth['enroll_portal_url'])
    elif pre_auth['result'] == "deny":
        # User is denied by policy setting
        print(pre_auth['status_msg'])
    else:
        print("Error: an unexpected error occurred")
        print(pre_auth)


if __name__ == '__main__':
    main()
