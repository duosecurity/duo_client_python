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
verify_api = duo_client.Verify(
    ikey=get_next_arg('Verify API integration key ("DI..."): '),
    skey=get_next_arg('integration secret key: '),
    host=get_next_arg('API hostname ("api-....duosecurity.com"): '),
)

# Please use your valid telephone number with country code, area
# code, and 7 digit number. For example: PHONE = '+1-313-555-5555'
PHONE_NUMBER = get_next_arg('phone number ("+1-313-555-5555"): ')

(pin, txid) = verify_api.call(phone=PHONE_NUMBER)
print 'Sent PIN: %s' % pin
state = ''
while state != 'ended':
    status_res = verify_api.status(txid=txid)
    print status_res['event'], 'event:', status_res['info']
    state = status_res['state']
