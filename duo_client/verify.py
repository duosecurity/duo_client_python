"""
Duo Security Verify API reference client implementation.

<http://www.duosecurity.com/docs/duoverify>
"""

import client

SIG_VERSION = 1

def call(ikey, skey, host, phone,
         ca=None):
    """
    Return a (PIN, txid) tuple from the response for a call API call.
    """
    response = client.call_json_api(
        ikey, skey, host, 'POST', '/verify/v1/call.json',
        ca=ca,
        sig_version=SIG_VERSION,
        phone=phone, message='The PIN is <pin>')
    return (response['pin'], response['txid'])

def status(ikey, skey, host, txid,
           ca=None):
    """
    Return the response for a status API call.
    """
    response = client.call_json_api(
        ikey, skey, host, 'GET', '/verify/v1/status.json',
        ca=ca,
        sig_version=SIG_VERSION,
        txid=txid)
    return response

def sms(ikey, skey, host, phone,
        ca=None):
    """
    Return the PIN from the response for a SMS API call.
    """
    response = client.call_json_api(
        ikey, skey, host, 'POST', '/verify/v1/sms.json',
        ca=ca,
        sig_version=SIG_VERSION,
        phone=phone, message='The PIN is <pin>')
    return response['pin']
