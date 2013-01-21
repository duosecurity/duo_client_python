#!/usr/bin/python
import sys

import duo_client

argv_iter = iter(sys.argv[1:])
def get_next_arg(prompt):
    try:
        return argv_iter.next()
    except StopIteration:
        return raw_input(prompt)

# You can find this information in the integrations section
# where you signed up for Duo.
VERIFY_API_CFG = {
    'ikey': get_next_arg('ikey ("DI..."): '),
    'skey': get_next_arg('integration secret key: '),
    'host': get_next_arg('API hostname ("api-....duosecurity.com"): '),
}

# Please use your valid telephone number with country code, area
# code, and 7 digit number. For example: PHONE = '+1-313-555-5555'
PHONE_NUMBER = get_next_arg('phone number ("+1-313-555-5555"): ')

(pin, txid) = duo_client.verify.call(phone=PHONE_NUMBER,
                                          **VERIFY_API_CFG)
print 'Sent PIN: %s' % pin
state = ''
while state != 'ended':
    status_res = duo_client.verify.status(txid=txid,
                                          **VERIFY_API_CFG)
    print status_res['event'], 'event:', status_res['info']
    state = status_res['state']
