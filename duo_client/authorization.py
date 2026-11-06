"""
Duo Security Authorization API reference client implementation.
"""
from dataclasses import dataclass
from typing import ClassVar, Optional

from . import client


@dataclass
class McpCapabilities:
    route_fragment: ClassVar[str] = 'mcp_capabilities'
    access_token: str
    mcp_server_id: str
    mcp_server_name: str = ''
    tool: Optional[str] = None


class Authorization(client.Client):
    def ping(self):
        """
        Determine if the Duo Authorization service is up and responding.

        Returns information about the service state: {
            'time': <int:UNIX timestamp>,
        }
        """
        return self.json_api_call('GET', '/authorize/v1/ping', {})

    def check(self):
        """
        Determine if the integration key, secret key, and signature
        generation are valid.

        Returns information about the service state: {
            'time': <int:UNIX timestamp>,
        }
        """
        return self.json_api_call('GET', '/authorize/v1/check', {})

    def evaluate(self, input: McpCapabilities):
        """
        Evaluate authorization policy for MCP server capabilities.

        Returns: {
            'allowed_capabilities': <list[str] or None>,
            'authorized': <bool or None>,
            'expires_at': <int:UNIX timestamp>,
            'user_id': <str>,
            'non_human_identity': <str>,
            'policy_version_id': <int or None>,
        }
        """
        params = {
            'access_token': input.access_token,
            'mcp_server_id': input.mcp_server_id,
            'mcp_server_name': input.mcp_server_name,
        }
        if input.tool is not None:
            params['tool'] = input.tool
        response = self.json_api_call('POST', f'/authorize/v1/{input.route_fragment}/evaluate', params)
        return {
            'allowed_capabilities': response.get('allowed_capabilities'),
            'authorized': response.get('authorized'),
            'expires_at': response.get('expires_at'),
            'user_id': response.get('user_id'),
            'non_human_identity': response.get('non_human_identity'),
            'policy_version_id': response.get('policy_version_id'),
        }
