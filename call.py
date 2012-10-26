#!/usr/bin/env python
"""
Demonstration of sending a PIN to a phone via voice, and polling for the
call status.
"""

import ConfigParser

import client

def call(ikey, skey, host, phone):
    """
    Return a (PIN, txid) tuple from the response for a call API call.
    """
    response = client.call_json_api(
        ikey, skey, host, 'POST', '/verify/v1/call.json',
        phone=phone, message='The PIN is <pin>')
    return (response['pin'], response['txid'])

def status(ikey, skey, host, txid):
    """
    Return the response for a status API call.
    """
    response = client.call_json_api(
        ikey, skey, host, 'GET', '/verify/v1/status.json',
        txid=txid)
    return response

if __name__ == '__main__':
    config = ConfigParser.ConfigParser()
    config.read('duo.conf')
    config_d = dict(config.items('duo'))
    ikey = config_d['ikey']
    skey = config_d['skey']
    host = config_d['host']
    config_d = dict(config.items('misc'))
    phone = config_d['phone']

    (pin, txid) = call(ikey, skey, host, phone)
    print 'Sent PIN: %s' % pin
    state = ''
    while state != 'ended':
        response = status(ikey, skey, host, txid)
        print response['info']
        state = response['state']
