#!/usr/bin/env python
"""
Demonstration of sending a PIN to a phone via SMS.
"""

import ConfigParser

import client

def sms(ikey, skey, host, phone):
    """
    Return the PIN from the response for a SMS API call.
    """
    response = client.call_json_api(
        ikey, skey, host, 'POST', '/verify/v1/sms.json',
        phone=[phone], message=['The PIN is <pin>'])
    return response['pin']

if __name__ == '__main__':
    config = ConfigParser.ConfigParser()
    config.read('duo.conf')
    config_d = dict(config.items('duo'))
    ikey = config_d['ikey']
    skey = config_d['skey']
    host = config_d['host']
    config_d = dict(config.items('misc'))
    phone = config_d['phone']

    pin = sms(ikey, skey, host, phone)
    print 'Sent PIN: %s' % pin
