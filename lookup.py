#!/usr/bin/env python
"""
Demonstration of looking up an IP address and phone number.
"""

import ConfigParser

import client

def lookup_phone(ikey, skey, host, phone):
    """
    Return the response for a phone lookup API call.
    """
    response = client.call_json_api(
        ikey, skey, host, 'GET', '/verify/v1/lookup/phone.json',
        phone=[phone])
    return response

def lookup_ip(ikey, skey, host, ip):
    """
    Return the response for an IP lookup API call.
    """
    response = client.call_json_api(
        ikey, skey, host, 'GET', '/verify/v1/lookup/ip.json',
        ip=[ip])
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
    ip = config_d['ip']

    response = lookup_phone(ikey, skey, host, phone)
    print 'phone information for %s:' % phone
    for (key, value) in response.items():
        print "%s: %s" % (key, value)
    response = lookup_ip(ikey, skey, host, ip)
    print
    print 'IP address information for %s:' % ip
    for (key, value) in response.items():
        print "%s: %s" % (key, value)
