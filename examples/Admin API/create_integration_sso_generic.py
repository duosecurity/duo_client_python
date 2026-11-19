#!/usr/bin/python
from __future__ import absolute_import
from __future__ import print_function
import pprint
import sys

import duo_client
from six.moves import input

argv_iter = iter(sys.argv[1:])
def get_next_arg(prompt):
    try:
        return next(argv_iter)
    except StopIteration:
        return input(prompt)

ikey = get_next_arg('Admin API integration key ("DI..."): ')
skey = get_next_arg('integration secret key: ')
host = get_next_arg('API hostname ("api-....duosecurity.com"): ')

# Configuration and information about objects to create.
admin_api = duo_client.Admin(
    ikey,
    skey,
    host,
)

integration = admin_api.create_integration(
    name='api-created integration',
    integration_type='sso-generic',
    sso={
        "saml_config": {
            "entity_id": "entity_id",
            "acs_urls": [
                {
                    "url": "https://example.com/acs",
                    "binding": None,
                    "isDefault": None,
                    "index": None,
                }
            ],
            "nameid_format": "urn:oasis:names:tc:SAML:1.1:nameid-format:unspecified",
            "nameid_attribute": "mail",
            "sign_assertion": False,
            "sign_response": True,
            "signing_algorithm": "http://www.w3.org/2001/04/xmldsig-more#rsa-sha256",
            "mapped_attrs": {},
            "relaystate": "https://example.com/relaystate",
            "slo_url": "https://example.com/slo",
            "spinitiated_url": "https://example.com/spurl",
            "static_attrs": {},
            "role_attrs": {
                "bob": {
                    "ted": ["DGS08MMO53GNRLSFW0D0", "DGETXINZ6CSJO4LRSVKV"],
                    "frank": ["DGETXINZ6CSJO4LRSVKV"],
                }
            },
            "attribute_transformations": {
                "attribute_1": 'use "<Username>"\nprepend text="dev-"',
                "attribute_2": 'use "<Email Address>"\nappend additional_attr="<First Name>"',
            }
        }
    },
)

print('Created integration:')
pprint.pprint(integration)
