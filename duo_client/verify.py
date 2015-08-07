"""
Duo Security Verify API reference client implementation.

<http://www.duosecurity.com/docs/duoverify>
"""
from __future__ import absolute_import
from . import client

class Verify(client.Client):
    def call(self, phone,
             extension=None,
             predelay=None,
             postdelay=None,
             message='The PIN is <pin>',
             digits=None):
        """
        Return a (PIN, txid) tuple from the response for a call API call.
        """
        params = {
            'phone': phone,
            'message': message,
        }
        if extension is not None:
            params['extension'] = extension
        if predelay is not None:
            params['predelay'] = predelay
        if postdelay is not None:
            params['postdelay'] = postdelay
        if digits is not None:
            params['digits'] = str(int(digits))
        response = self.json_api_call('POST',
                                      '/verify/v1/call',
                                      params)
        return (response['pin'], response['txid'])

    def status(self, txid):
        """
        Return the response for a status API call.
        """
        params = {
            'txid': txid,
        }
        response = self.json_api_call('GET',
                                      '/verify/v1/status',
                                      params)
        return response

    def sms(self, phone,
            message='The PIN is <pin>',
            digits=None):
        """
        Return the PIN from the response for a SMS API call.
        """
        params = {
            'phone': phone,
            'message': message,
        }
        if digits is not None:
            params['digits'] = str(int(digits))
        response = self.json_api_call('POST',
                                      '/verify/v1/sms',
                                      params)
        return response['pin']
