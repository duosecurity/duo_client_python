"""
Example of Duo Auth API uaer authentication with synchronous request/response using an assigned token
as the MFA factor
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

    print("\n" + "=" * 30)
    pprint(f"Pre-Auth result: {pre_auth}")
    print("=" * 30 + "\n")

    for device in pre_auth['devices']:
        pprint(device)
        print()

    if pre_auth['result'] == "auth":
        try:
            print(f"Executing authentication action for {inputs['USERNAME']}...")
            # Prompt for the hardware token passcode
            passcode = _get_next_arg('Duo token passcode: ')
            auth = auth_client.auth(factor="passcode", username=inputs['USERNAME'], passcode=passcode)
            print(f"\n{auth['status_msg']}")
        except Exception as e_str:
            print(e_str)
    else:
        print(pre_auth)


if __name__ == '__main__':
    main()
