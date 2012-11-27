"""
Duo Security REST API reference client implementation.

<http://www.duosecurity.com/docs/duorest>
"""

import client


SIG_VERSION = 1

FACTOR_AUTO = "auto"
FACTOR_PASSCODE = "passcode"
FACTOR_PHONE = "phone"
FACTOR_SMS = "sms"
FACTOR_PUSH = "push"

PHONE1 = "phone1"
PHONE2 = "phone2"
PHONE3 = "phone3"
PHONE4 = "phone4"
PHONE5 = "phone5"


def ping(ikey, skey, host, ca=None):
    """
    Returns True if and only if the Duo service is up and responding.
    """
    path = "/rest/v1/ping"
    response = client.call_json_api(ikey, skey, host, 'GET', path, ca,
                                    sig_version=SIG_VERSION)
    return response == 'pong'


def check(ikey, skey, host, ca=None):
    """
    Returns True if and only if the integration key, secret key, and
    signature generation are valid.
    """
    path = "/rest/v1/check"
    response = client.call_json_api(ikey, skey, host, 'GET', path, ca,
                                    sig_version=SIG_VERSION)
    return response == 'valid'


def preauth(ikey, skey, host, username, ca=None):
    path = "/rest/v1/preauth"
    response = client.call_json_api(ikey, skey, host, "POST", path, ca,
                                    sig_version=SIG_VERSION, user=username)
    return response


def auth(ikey, skey, host, username, factor=FACTOR_PHONE,
         auto=None, passcode=None, phone=PHONE1, pushinfo=None,
         async=False, ca=None):
    """
    Returns True if authentication was a success, else False.

    If 'async' is True, returns txid of the authentication transaction.
    """
    path = "/rest/v1/auth"
    kwargs = {}
    if async:
        kwargs['async'] = '1'

    if factor == FACTOR_AUTO:
        kwargs['auto'] = auto
    elif factor == FACTOR_PASSCODE:
        kwargs['code'] = passcode
    elif factor == FACTOR_PHONE:
        kwargs['phone'] = phone
    elif factor == FACTOR_SMS:
        kwargs['phone'] = phone
    elif factor == FACTOR_PUSH:
        kwargs['phone'] = phone

    response = client.call_json_api(ikey, skey, host, "POST", path, ca,
                                    sig_version=SIG_VERSION,
                                    user=username,
                                    factor=factor,
                                    **kwargs)
    if async:
        return response['txid']
    return response['result'] == 'allow'


def status(ikey, skey, host, txid, ca=None):
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
    path = "/rest/v1/status"
    response = client.call_json_api(ikey, skey, host, "GET", path, ca,
                                    sig_version=SIG_VERSION, txid=txid)
    complete = False
    success = False
    if "result" in response:
        complete = True
        success = response['result'] == 'allow'
    description = response['status']

    return (complete, success, description)
