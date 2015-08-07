"""
Duo Security Auth API v1 reference client implementation.

<http://www.duosecurity.com/docs/authapi-v1>
"""
from __future__ import absolute_import

from . import client


FACTOR_AUTO = 'auto'
FACTOR_PASSCODE = 'passcode'
FACTOR_PHONE = 'phone'
FACTOR_SMS = 'sms'
FACTOR_PUSH = 'push'

PHONE1 = 'phone1'
PHONE2 = 'phone2'
PHONE3 = 'phone3'
PHONE4 = 'phone4'
PHONE5 = 'phone5'


class AuthV1(client.Client):
    auth_details = False

    def ping(self):
        """
        Returns True if and only if the Duo service is up and responding.
        """
        response = self.json_api_call('GET', '/rest/v1/ping', {})
        return response == 'pong'


    def check(self):
        """
        Returns True if and only if the integration key, secret key, and
        signature generation are valid.
        """
        response = self.json_api_call('GET', '/rest/v1/check', {})
        return response == 'valid'


    def logo(self):
        """
        Retrieve the user-supplied logo.

        Returns the logo on success, raises RuntimeError on failure.
        """
        response, data = self.api_call('GET', '/rest/v1/logo', {})
        content_type = response.getheader('Content-Type')
        if content_type and content_type.startswith('image/'):
            return data
        else:
            return self.parse_json_response(response, data)



    def preauth(self, username,
                ipaddr=None):
        params = {
            'user': username,
        }
        if ipaddr is not None:
            params['ipaddr'] = ipaddr
        response = self.json_api_call('POST', '/rest/v1/preauth', params)
        return response


    def auth(self, username,
             factor=FACTOR_PHONE,
             auto=None,
             passcode=None,
             phone=PHONE1,
             pushinfo=None,
             ipaddr=None,
             async=False):
        """
        Returns True if authentication was a success, else False.

        If 'async' is True, returns txid of the authentication transaction.
        """
        params = {
            'user': username,
            'factor': factor,
        }
        if async:
            params['async'] = '1'
        if pushinfo is not None:
            params['pushinfo'] = pushinfo
        if ipaddr is not None:
            params['ipaddr'] = ipaddr

        if factor == FACTOR_AUTO:
            params['auto'] = auto
        elif factor == FACTOR_PASSCODE:
            params['code'] = passcode
        elif factor == FACTOR_PHONE:
            params['phone'] = phone
        elif factor == FACTOR_SMS:
            params['phone'] = phone
        elif factor == FACTOR_PUSH:
            params['phone'] = phone

        response = self.json_api_call('POST', '/rest/v1/auth', params)
        if self.auth_details:
            return response
        if async:
            return response['txid']
        return response['result'] == 'allow'


    def status(self, txid):
        """
        Returns a 3-tuple:
            (complete, success, description)

            complete - True if the authentication request has
                       completed, else False.
            success - True if the authentication request has
                      completed and was a success, else False.
            description - A string describing the current status of the
                          authentication request.
        """
        params = {
            'txid': txid,
        }
        response = self.json_api_call('GET', '/rest/v1/status', params)
        complete = False
        success = False
        if 'result' in response:
            complete = True
            success = response['result'] == 'allow'
        description = response['status']

        return (complete, success, description)
