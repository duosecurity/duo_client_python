"""
Example of Duo Auth API user authentication using asynchronous resquest/response methods
"""

import duo_client
import sys
import getpass


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
            print(f"Executing authentication action for {inputs['USERNAME']}...")
            auth = auth_client.auth(factor="push", username=inputs['USERNAME'], device="auto", async_txn=True)
            if 'txid' in auth:
                waiting = True
                # Collect the authentication result
                print("Getting authentication result...")
                # Repeat long polling for async authentication status until no longer in a 'waiting' state
                while waiting is True:
                    # Poll Duo Auth API for the status of the async authentication based upon transaction ID
                    auth_status = auth_client.auth_status(auth['txid'])
                    print(f"Auth status: {auth_status}")
                    if auth_status['waiting'] is not True:
                        # Waiting for response too async authentication is no longer 'True', so break the loop
                        waiting = False
                # Parse response for the 'status' dictionary key to determine whether to allow or deny
                print(auth_status)
            else:
                # Some kind of unexpected error occurred
                print(f"Error: an unknown error occurred attempting authentication for [{inputs['USERNAME']}]")
        except Exception as e_str:
            print(e_str)
    else:
        print(pre_auth['status_msg'])


if __name__ == '__main__':
    main()
