"""
Example of Duo Authorization API MCP capabilities evaluation
"""

from argparse import ArgumentParser, Namespace
import duo_client
from duo_client.authorization import McpCapabilities
import getpass


def _get_arg(args: Namespace, name: str, prompt: str, secure=False):
    """Read arg from CLI flags or stdin, using getpass when sensitive information should not be echoed to tty"""
    value = getattr(args, name)
    if value is not None:
        return value

    if secure is True:
        return getpass.getpass(prompt)
    else:
        return input(prompt)


def prompt_for_credentials(args: Namespace) -> dict:
    """Collect required API credentials from command line prompts

    :return: dictionary containing Duo Authorization API ikey, skey and hostname strings
    """

    ikey = _get_arg(args, "ikey", 'Duo Authorization API integration key ("DI..."): ')
    skey = _get_arg(args, "skey", 'Duo Authorization API integration secret key: ', secure=True)
    host = _get_arg(args, "api_host", 'Duo Authorization API hostname ("api-....duosecurity.com"): ')
    access_token = _get_arg(args, "access_token", 'Access token: ', secure=True)
    mcp_server_id = _get_arg(args, "mcp_server_id", 'MCP Server ID: ')

    return {
        "IKEY": ikey,
        "SKEY": skey,
        "APIHOST": host,
        "ACCESS_TOKEN": access_token,
        "MCP_SERVER_ID": mcp_server_id,
    }


def main():
    """Main program entry point"""

    parser = ArgumentParser()
    parser.add_argument("--ikey", type=str)
    parser.add_argument("--skey", type=str)
    parser.add_argument("--api-host", type=str)
    parser.add_argument("--access-token", type=str)
    parser.add_argument("--mcp-server-id", type=str)
    parser.add_argument("--mcp-server-name", type=str, default='')
    parser.add_argument("--tool", type=str, default=None)
    args = parser.parse_args()

    inputs = prompt_for_credentials(args)

    authz_client = duo_client.Authorization(
        ikey=inputs['IKEY'],
        skey=inputs['SKEY'],
        host=inputs['APIHOST'],
    )

    # Verify that the Duo service is available
    duo_ping = authz_client.ping()
    if 'time' in duo_ping:
        print("\nDuo Authorization service check completed successfully.")
    else:
        print(f"Error: {duo_ping}")

    # Verify that IKEY and SKEY information provided are valid
    duo_check = authz_client.check()
    if 'time' in duo_check:
        print("IKEY and SKEY provided have been verified.")
    else:
        print(f"Error: {duo_check}")

    # Evaluate MCP capabilities
    capabilities = McpCapabilities(
        access_token=inputs['ACCESS_TOKEN'],
        mcp_server_id=inputs['MCP_SERVER_ID'],
        mcp_server_name=args.mcp_server_name,
        tool=args.tool,
    )

    print(f"\nEvaluating MCP capabilities for server {inputs['MCP_SERVER_ID']}...")
    result = authz_client.evaluate(capabilities)

    print(f"\nAuthorized: {result['authorized']}")
    print(f"Allowed capabilities: {result['allowed_capabilities']}")
    print(f"User ID: {result['user_id']}")
    print(f"Non-human identity: {result['non_human_identity']}")
    print(f"Policy version ID: {result['policy_version_id']}")
    print(f"Expires at: {result['expires_at']}")


if __name__ == '__main__':
    main()
