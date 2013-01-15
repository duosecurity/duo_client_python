"""
Duo Security Administration API reference client implementation.

<http://www.duosecurity.com/docs/adminapi>


USERS

User objects are returned in the following format:

        {"username": <str:username>,
         "user_id": <str:user id>,
         "realname": <str:real name>,
         "status": <str:status>,
         "notes": <str:notes>,
         "last_login": <int:unix timestamp>,
         "phones": [<phone object>, ...],
         "tokens": [<token object>, ...]}

User status is one of:

        USER_STATUS_ACTIVE, USER_STATUS_BYPASS, USER_STATUS_DISABLED,
        USER_STATUS_LOCKED_OUT

Note: USER_STATUS_LOCKED_OUT can only be set by the system. You cannot
      set a user to be in the USER_STATUS_LOCKED_OUT state.


PHONES

Phone objects are returned in the following format:

    {"phone_id": <str:phone id>,
     "number": <str:phone number>,
     "extension": <str:phone extension>|'',
     "predelay": <str:predelay in seconds>|None,
     "postdelay": <str:postdelay in seconds>|None,
     "type": <str:phone type>|"Unknown",
     "platform": <str:phone platform>|"Unknown",
     "activated": <bool:is push enabled>,
     "sms_passcodes_sent": <bool:have sms OTP been sent>,
     "users": [<user object>, ...]}


TOKENS

Token objects are returned in the following format:

    {"type": <str:token type>,
     "serial": <str:token serial number>,
     "token_id": <str:token id>,
     "users": [<user object>, ...]}

Token type is one of:

    TOKEN_HOTP_6, TOKEN_HOTP_8, TOKEN_YUBIKEY


SETTINGS

Settings objects are returned in the following format:

    {'inactive_user_expiration': <int:days until expiration>|0,
     'sms_message': <str:sms message>,
     'name': <str:name>,
     'sms_batch': <int:sms batch size>,
     'lockout_threshold': <int:lockout threshold>
     'sms_expiration': <int:minutes until expiration>|0,
     'sms_refresh': <bool:is sms refresh enambed (0|1)>


INTEGRATIONS

Integration objects are returned in the following format:

    {'adminapi_admins': <bool:admins permission (0|1)>,
     'adminapi_info': <bool:info permission (0|1)>,
     'adminapi_integrations': <bool:integrations permission (0|1)>,
     'adminapi_read_log': <bool:read log permission (0|1)>,
     'adminapi_read_resource': <bool:read resource permission (0|1)>,
     'adminapi_settings': <bool:settings permission (0|1)>,
     'adminapi_write_resource': <bool:write resource permission (0|1)>,
     'enroll_policy': <str:enroll policy (enroll|allow|deny)>,
     'greeting': <str:voice greeting>,
     'integration_key': <str:integration key>,
     'name': <str:integration name>,
     'notes': <str:notes>,
     'secret_key': <str:secret key>,
     'type': <str:integration type>,
     'visual_style': <str:visual style>}

See the adminapi docs for possible values for enroll_policy, visual_style,
and type.

ERRORS

Methods will raise a RuntimeError when an error is encountered. When
the call returns a HTTP status other than 200, error will be populated with
the following fields:

    message - String description of the error encountered such as
              "Received 404 Not Found"
    status - HTTP status such as 404 (int)
    reason - Status description such as "Not Found"
    data - Detailed error code such as
           {"code": 40401, "message": "Resource not found", "stat": "FAIL"}
"""

import urllib

import client

USER_STATUS_ACTIVE = 'active'
USER_STATUS_BYPASS = 'bypass'
USER_STATUS_DISABLED = 'disabled'
USER_STATUS_LOCKED_OUT = 'locked out'

TOKEN_HOTP_6 = 'h6'
TOKEN_HOTP_8 = 'h8'
TOKEN_YUBIKEY = 'yk'


def get_administrator_log(ikey, skey, host, ca=None, mintime=0):
    """
    Returns administrator log events.

    ikey - Admin API integration ikey
    skey - Admin API integration skey
    host - Duo host
    ca - Optional CA cert
    mintime - Fetch events only >= mintime (to avoid duplicate
              records that have already been fetched)

    Returns:
        [
            {'timestamp': <int:unix timestamp>,
             'eventtype': "administrator",
             'host': <str:hostname>,
             'username': <str:username>,
             'action': <str:action>,
             'object': <str:object name>|None,
             'description': <str:description>|None}, ...
        ]

    <action> is one of:
        'admin_login',
        'admin_create', 'admin_update', 'admin_delete',
        'customer_update',
        'group_create', 'group_update', 'group_delete',
        'integration_create', 'integration_update', 'integration_delete',
        'phone_create', 'phone_update', 'phone_delete',
        'user_create', 'user_update', 'user_delete'

    Raises RuntimeError on error.
    """
    # Sanity check mintime as unix timestamp, then transform to string
    mintime = str(int(mintime))

    response = client.call_json_api(
        ikey, skey, host, 'GET', '/admin/v1/logs/administrator.json', ca,
        mintime=mintime)
    for row in response:
        row['eventtype'] = "administrator"
        row['host'] = host
    return response


def get_authentication_log(ikey, skey, host, ca=None, mintime=0):
    """
    Returns authentication log events.

    ikey - Admin API integration ikey
    skey - Admin API integration skey
    host - Duo host
    ca - Optional CA cert
    mintime - Fetch events only >= mintime (to avoid duplicate
              records that have already been fetched)

    Returns:
        [
            {'timestamp': <int:unix timestamp>,
             'eventtype': "authentication",
             'host': <str:host>,
             'username': <str:username>,
             'factor': <str:factor>,
             'result': <str:result>,
             'ip': <str:ip address>,
             'integration': <str:integration>}, ...
        ]

    Raises RuntimeError on error.
    """
    # Sanity check mintime as unix timestamp, then transform to string
    mintime = str(int(mintime))

    response = client.call_json_api(
        ikey, skey, host, 'GET', '/admin/v1/logs/authentication.json', ca,
        mintime=mintime)
    for row in response:
        row['eventtype'] = "authentication"
        row['host'] = host
    return response


def get_telephony_log(ikey, skey, host, ca=None, mintime=0):
    """
    Returns telephony log events.

    ikey - Admin API integration ikey
    skey - Admin API integration skey
    host - Duo host
    ca - Optional CA cert
    mintime - Fetch events only >= mintime (to avoid duplicate
              records that have already been fetched)

    Returns:
        [
            {'timestamp': <int:unix timestamp>,
             'eventtype': "telephony",
             'host': <str:host>,
             'context': <str:context>,
             'type': <str:type>,
             'phone': <str:phone number>,
             'credits': <str:credits>}, ...
        ]

    Raises RuntimeError on error.
    """
    # Sanity check mintime as unix timestamp, then transform to string
    mintime = str(int(mintime))

    response = client.call_json_api(
        ikey, skey, host, 'GET', '/admin/v1/logs/telephony.json', ca,
        mintime=mintime)
    for row in response:
        row['eventtype'] = "telephony"
        row['host'] = host
    return response


def get_users(ikey, skey, host, ca=None):
    """
    Returns list of users.

    ikey - Admin API integration ikey
    skey - Admin API integration skey
    host - Duo host
    ca - Optional CA cert

    Returns list of user objects.

    Raises RuntimeError on error.
    """
    response = client.call_json_api(
        ikey, skey, host, 'GET', '/admin/v1/users', ca)
    return response


def get_user_by_id(ikey, skey, host, user_id, ca=None):
    """
    Returns user specified by user_id.

    ikey - Admin API integration ikey
    skey - Admin API integration skey
    host - Duo host
    user_id - User to fetch
    ca - Optional CA cert

    Returns user object.

    Raises RuntimeError on error.
    """
    user_id = urllib.quote_plus(str(user_id))
    url = '/admin/v1/users/' + user_id
    response = client.call_json_api(ikey, skey, host, 'GET', url, ca)
    return response


def get_users_by_name(ikey, skey, host, username, ca=None):
    """
    Returns user specified by username.

    ikey - Admin API integration ikey
    skey - Admin API integration skey
    host - Duo host
    username - User to fetch
    ca - Optional CA cert

    Returns a list of 0 or 1 user objects.

    Raises RuntimeError on error.
    """
    url = '/admin/v1/users'
    response = client.call_json_api(ikey, skey, host, 'GET', url, ca,
                                    username=username)
    return response


def add_user(ikey, skey, host, username, realname=None, status=None,
             notes=None, ca=None):
    """
    Adds a user.

    ikey - Admin API integration ikey
    skey - Admin API integration skey
    host - Duo host
    username - Username
    realname - User's real name (optional)
    status - User's status, defaults to USER_STATUS_ACTIVE
    notes - Comment field (optional)
    ca - Optional CA cert

    Returns newly created user object.

    Raises RuntimeError on error.
    """
    url = '/admin/v1/users'
    kwargs = {'username': username}
    if realname is not None:
        kwargs['realname'] = realname
    if status is not None:
        kwargs['status'] = status
    if notes is not None:
        kwargs['notes'] = notes
    response = client.call_json_api(ikey, skey, host, 'POST', url, ca,
                                    **kwargs)
    return response


def update_user(ikey, skey, host, user_id, username=None, realname=None,
                status=None, notes=None, ca=None):
    """
    Update username, realname, status, or notes for a user.

    ikey - Admin API integration ikey
    skey - Admin API integration skey
    host - Duo host
    user_id - User ID
    username - Username (optional)
    realname - User's real name (optional)
    status - User's status, defaults to USER_STATUS_ACTIVE
    notes - Comment field (optional)
    ca - Optional CA cert

    Returns updated user object.

    Raises RuntimeError on error.
    """
    url = '/admin/v1/users/' + user_id
    kwargs = {}
    if username is not None:
        kwargs['username'] = username
    if realname is not None:
        kwargs['realname'] = realname
    if status is not None:
        kwargs['status'] = status
    if notes is not None:
        kwargs['notes'] = notes
    response = client.call_json_api(ikey, skey, host, 'POST', url, ca,
                                    **kwargs)
    return response


def delete_user(ikey, skey, host, user_id, ca=None):
    """
    Deletes a user. If the user is already deleted, does nothing.

    ikey - Admin API integration ikey
    skey - Admin API integration skey
    host - Duo host
    user_id - User ID
    ca - Optional CA cert

    Returns nothing.

    Raises RuntimeError on error.
    """
    url = '/admin/v1/users/' + user_id
    client.call_json_api(ikey, skey, host, 'DELETE', url, ca)


def get_user_bypass_codes(ikey, skey, host, user_id, count=10, valid_secs=0,
                          ca=None):
    """
    Replace a user's bypass codes with new codes.

    ikey - Admin API integration ikey
    skey - Admin API integration skey
    host - Duo host
    user_id - User ID
    count - Number of new codes to generate
    valid_secs - Seconds before codes expire (if 0 they will never expire)
    ca - Optional CA cert

    Returns a list of newly created codes.

    Raises RuntimeError on error.
    """
    url = '/admin/v1/users/' + user_id + '/bypass_codes'
    count = str(int(count))
    valid_secs = str(int(valid_secs))
    return client.call_json_api(ikey, skey, host, 'POST', url, ca=ca,
                                count=count,
                                valid_secs=valid_secs)


def get_user_phones(ikey, skey, host, user_id,
                    ca=None):
    """
    Returns an array of phones associated with the user.

    ikey - Admin API integration ikey
    skey - Admin API integration skey
    host - Duo host
    user_id - User ID
    ca - Optional CA cert

    Returns list of phone objects.

    Raises RuntimeError on error.
    """
    url = '/admin/v1/users/' + user_id + '/phones'
    return client.call_json_api(ikey, skey, host, 'GET', url, ca=ca)


def add_user_phone(ikey, skey, host, user_id, phone_id,
                   ca=None):
    """
    Associates a phone with a user.

    ikey - Admin API integration ikey
    skey - Admin API integration skey
    host - Duo host
    user_id - User ID
    phone_id - Phone ID
    ca - Optional CA cert

    Returns nothing.

    Raises RuntimeError on error.
    """
    url = '/admin/v1/users/' + user_id + '/phones'
    return client.call_json_api(ikey, skey, host, 'POST', url,
                                phone_id=phone_id,
                                ca=ca)


def delete_user_phone(ikey, skey, host, user_id, phone_id,
                      ca=None):
    """
    Dissociates a phone from a user.

    ikey - Admin API integration ikey
    skey - Admin API integration skey
    host - Duo host
    user_id - User ID
    phone_id - Phone ID
    ca - Optional CA cert

    Returns nothing.

    Raises RuntimeError on error.
    """
    url = '/admin/v1/users/' + user_id + '/phones/' + phone_id
    return client.call_json_api(ikey, skey, host, 'DELETE', url,
                                ca=ca)


def get_user_tokens(ikey, skey, host, user_id,
                    ca=None):
    """
    Returns an array of hardware tokens associated with the user.

    ikey - Admin API integration ikey
    skey - Admin API integration skey
    host - Duo host
    user_id - User ID
    ca - Optional CA cert

    Returns list of hardware token objects.

    Raises RuntimeError on error.
    """
    url = '/admin/v1/users/' + user_id + '/tokens'
    return client.call_json_api(ikey, skey, host, 'GET', url, ca=ca)


def add_user_token(ikey, skey, host, user_id, token_id,
                   ca=None):
    """
    Associates a hardware token with a user.

    ikey - Admin API integration ikey
    skey - Admin API integration skey
    host - Duo host
    user_id - User ID
    token_id - Token ID
    ca - Optional CA cert

    Returns nothing.

    Raises RuntimeError on error.
    """
    url = '/admin/v1/users/' + user_id + '/tokens'
    return client.call_json_api(ikey, skey, host, 'POST', url,
                                token_id=token_id,
                                ca=ca)


def delete_user_token(ikey, skey, host, user_id, token_id,
                      ca=None):
    """
    Dissociates a hardware token from a user.

    ikey - Admin API integration ikey
    skey - Admin API integration skey
    host - Duo host
    user_id - User ID
    token_id - Hardware token ID
    ca - Optional CA cert

    Returns nothing.

    Raises RuntimeError on error.
    """
    url = '/admin/v1/users/' + user_id + '/tokens/' + token_id
    return client.call_json_api(ikey, skey, host, 'DELETE', url,
                                ca=ca)


def get_phones(ikey, skey, host, ca=None):
    """
    Returns list of phones.

    ikey - Admin API integration ikey
    skey - Admin API integration skey
    host - Duo host
    ca - Optional CA cert

    Returns list of phone objects.

    Raises RuntimeError on error.
    """
    response = client.call_json_api(
        ikey, skey, host, 'GET', '/admin/v1/phones', ca)
    return response


def get_phone_by_id(ikey, skey, host, phone_id, ca=None):
    """
    Returns a phone specified by phone_id.

    ikey - Admin API integration ikey
    skey - Admin API integration skey
    host - Duo host
    phone_id - Phone ID
    ca - Optional CA cert

    Returns phone object.

    Raises RuntimeError on error.
    """
    url = '/admin/v1/phones/' + phone_id
    response = client.call_json_api(
        ikey, skey, host, 'GET', url, ca)
    return response


def get_phones_by_number(ikey, skey, host, number, extension=None, ca=None):
    """
    Returns a phone specified by number and extension.

    ikey - Admin API integration ikey
    skey - Admin API integration skey
    host - Duo host
    number - Phone number
    extension - Phone number extension (optional)
    ca - Optional CA cert

    Returns list of 0 or 1 phone objects.

    Raises RuntimeError on error.
    """
    url = '/admin/v1/phones'
    kwargs = {'number': number}
    if extension is not None:
        kwargs['extension'] = extension
    response = client.call_json_api(
        ikey, skey, host, 'GET', url, ca, **kwargs)
    return response


def add_phone(ikey, skey, host, number,
              extension=None,
              type=None,
              platform=None,
              predelay=None,
              postdelay=None,
              ca=None):
    """
    Adds a phone.

    ikey - Admin API integration ikey
    skey - Admin API integration skey
    host - Duo host
    number - Phone number
    extension - Phone number extension (optional)
    type - The phone type.
    platform - The phone platform.
    predelay - Number of seconds to wait after the number picks up
               before dialing the extension.
    postdelay - Number of seconds to wait after the extension is
                dialed before the speaking the prompt.
    ca - Optional CA cert

    Returns phone object.

    Raises RuntimeError on error.
    """
    url = '/admin/v1/phones'
    kwargs = {'number': number}
    if extension is not None:
        kwargs['extension'] = extension
    if type is not None:
        kwargs['type'] = type
    if platform is not None:
        kwargs['platform'] = platform
    if predelay is not None:
        kwargs['predelay'] = predelay
    if postdelay is not None:
        kwargs['postdelay'] = postdelay
    response = client.call_json_api(
        ikey, skey, host, 'POST', url, ca, **kwargs)
    return response


def delete_phone(ikey, skey, host, phone_id, ca=None):
    """
    Deletes a phone. If the phone has already been deleted, does nothing.

    ikey - Admin API integration ikey
    skey - Admin API integration skey
    host - Duo host
    phone_id - Phone ID.
    ca - Optional CA cert

    Returns nothing.

    Raises RuntimeError on error.
    """
    url = '/admin/v1/phones/' + phone_id
    client.call_json_api(ikey, skey, host, 'DELETE', url, ca)


def send_sms_activation_to_phone(ikey, skey, host, phone_id,
                                 valid_secs=None,
                                 install=None,
                                 installation_msg=None,
                                 activation_msg=None,
                                 ca=None):
    """
    Generate a Duo Mobile activation code and send it to the phone via
    SMS, optionally sending an additional message with a URL to
    install Duo Mobile.

    ikey - Admin API integration ikey
    skey - Admin API integration skey
    host - Duo host
    phone_id - Phone ID.
    valid_secs - The number of seconds activation code should be valid for.
                 Default: 86400 seconds (one day).
    install - '1' to also send an installation SMS message before the
              activation message; '0' to not send. Default: '0'.
    installation_msg - Custom installation message template to send to
                       the user if install was 1. Must contain
                       <insturl>, which is replaced with the
                       installation URL.
    activation_msg - Custom activation message template. Must contain
                     <acturl>, which is replaced with the activation URL.
    ca - Optional CA cert

    Returns: {
        "activation_msg": "To activate the Duo Mobile app, click this link: https://m-eval.duosecurity.com/iphone/7dmi4Oowz5g3J47FARLs",
        "installation_msg": "Welcome to Duo! To install the Duo Mobile app, click this link: http://m-eval.duosecurity.com",
        "valid_secs": 3600
    }

    Raises RuntimeError on error.
    """
    url = '/admin/v1/phones/' + phone_id + '/send_sms_activation'
    kwargs = {}
    if valid_secs is not None:
        kwargs['valid_secs'] = valid_secs
    if install is not None:
        kwargs['install'] = str(install)
    if installation_msg is not None:
        kwargs['installation_msg'] = installation_msg
    if activation_msg is not None:
        kwargs['activation_msg'] = activation_msg
    return client.call_json_api(ikey, skey, host, 'POST', url, ca,
                                **kwargs)


def get_tokens(ikey, skey, host, ca=None):
    """
    Returns list of tokens.

    ikey - Admin API integration ikey
    skey - Admin API integration skey
    host - Duo host
    ca - Optional CA cert

    Returns list of token objects.
    """
    response = client.call_json_api(
        ikey, skey, host, 'GET', '/admin/v1/tokens', ca)
    return response


def get_token_by_id(ikey, skey, host, token_id, ca=None):
    """
    Returns a token.

    ikey - Admin API integration ikey
    skey - Admin API integration skey
    host - Duo host
    token_id - Token ID
    ca - Optional CA cert

    Returns a token object.
    """
    url = '/admin/v1/tokens/' + token_id
    response = client.call_json_api(
        ikey, skey, host, 'GET', url, ca)
    return response


def get_tokens_by_serial(ikey, skey, host, type, serial, ca=None):
    """
    Returns a token.

    ikey - Admin API integration ikey
    skey - Admin API integration skey
    host - Duo host
    type - Token type, one of TOKEN_HOTP_6, TOKEN_HOTP_8, TOKEN_YUBIKEY
    serial - Token serial number
    ca - Optional CA cert

    Returns a list of 0 or 1 token objects.
    """
    url = '/admin/v1/tokens'
    response = client.call_json_api(
        ikey, skey, host, 'GET', url, ca, type=type, serial=serial)
    return response


def delete_token(ikey, skey, host, token_id, ca=None):
    """
    Deletes a token. If the token is already deleted, does nothing.

    ikey - Admin API integration ikey
    skey - Admin API integration skey
    host - Duo host
    token_id - Token ID
    ca - Optional CA cert

    Returns nothing on success.
    """
    url = '/admin/v1/tokens/' + token_id
    client.call_json_api(ikey, skey, host, 'DELETE', url, ca)


def add_hotp6_token(ikey, skey, host, serial, secret, ca=None):
    """
    Add a HOTP6 token.

    ikey - Admin API integration ikey
    skey - Admin API integration skey
    host - Duo host
    serial - Token serial number
    secret - HOTP secret
    ca - Optional CA cert

    Returns newly added token object.
    """
    url = '/admin/v1/tokens'
    kwargs = {'type': 'h6', 'serial': serial, 'secret': secret}
    response = client.call_json_api(ikey, skey, host, 'POST', url, ca,
                                    **kwargs)
    return response


def add_hotp8_token(ikey, skey, host, serial, secret, ca=None):
    """
    Add a HOTP8 token.

    ikey - Admin API integration ikey
    skey - Admin API integration skey
    host - Duo host
    serial - Token serial number
    secret - HOTP secret
    ca - Optional CA cert

    Returns newly added token object.
    """
    url = '/admin/v1/tokens'
    kwargs = {'type': 'h8', 'serial': serial, 'secret': secret}
    response = client.call_json_api(ikey, skey, host, 'POST', url, ca,
                                    **kwargs)
    return response


def add_yubikey_token(ikey, skey, host, serial, private_id, aes_key, ca=None):
    """
    Add a Yubikey AES token.

    ikey - Admin API integration ikey
    skey - Admin API integration skey
    host - Duo host
    serial - Token serial number
    secret - HOTP secret
    ca - Optional CA cert

    Returns newly added token object.
    """
    url = '/admin/v1/tokens'
    kwargs = {'type': 'yk', 'serial': serial, 'private_id': private_id,
              'aes_key': aes_key}
    response = client.call_json_api(ikey, skey, host, 'POST', url, ca,
                                    **kwargs)
    return response


def resync_hotp_token(ikey, skey, host, token_id, code1, code2, code3,
                      ca=None):
    """
    Resync HOTP counter. The user must generate 3 consecutive OTP
    from their token and input them as code1, code2, and code3. This
    function will scan ahead in the OTP sequence to find a counter
    that resyncs with those 3 codes.

    ikey - Admin API integration ikey
    skey - Admin API integration skey
    host - Duo host
    token_id - Token ID
    code1 - First OTP from token
    code2 - Second OTP from token
    code3 - Third OTP from token
    ca - Optional CA cert

    Returns nothing on success.
    """
    url = '/admin/v1/tokens/' + token_id + '/resync'
    kwargs = {'code1': code1, 'code2': code2, 'code3': code3}
    client.call_json_api(ikey, skey, host, 'POST', url, ca, **kwargs)


def get_settings(ikey, skey, host, ca=None):
    """
    Returns customer settings.

    ikey - Admin API integration ikey
    skey - Admin API integration skey
    host - Duo host
    ca - Optional CA cert

    Returns a settings object.

    Raises RuntimeError on error.
    """

    url = '/admin/v1/settings'
    response = client.call_json_api(ikey, skey, host, 'GET', url, ca)

    return response


def update_settings(ikey, skey, host, ca=None,
                    lockout_threshold=None,
                    inactive_user_expiration=None,
                    sms_batch=None,
                    sms_expiration=None,
                    sms_refresh=None,
                    sms_message=None,
                    fraud_email=None,
                    keypress_confirm=None,
                    keypress_fraud=None,
                    timezone=None,
                    caller_id=None):
    """
    Update settings.

    ikey - Admin API integration ikey
    skey - Admin API integration skey
    host - Duo host
    ca - Optional CA cert
    lockout_threshold - <int:number of attempts>|None
    inactive_user_expiration - <int:number of days>|None
    sms_batch - <int:batch size>|None
    sms_expiration - <int:minutes>|None
    sms_refresh - True|False|None
    sms_message - <str:message>|None
    fraud_email - <str:email address>|None
    keypress_confirm - <str:0-9, #, or *>|None
    keypress_fraud - <str:0-9, #, or *>|None
    timezone - <str:IANA timezone>|NOne
    caller_id - <str:phone number>

    Returns updated settings object.

    Raises RuntimeError on error.

    """
    url = '/admin/v1/settings'
    kwargs = {}
    if lockout_threshold is not None:
        kwargs['lockout_threshold'] = str(lockout_threshold)
    if inactive_user_expiration is not None:
        kwargs['inactive_user_expiration'] = str(inactive_user_expiration)
    if sms_batch is not None:
        kwargs['sms_batch'] = str(sms_batch)
    if sms_expiration is not None:
        kwargs['sms_expiration'] = str(sms_expiration)
    if sms_refresh is not None:
        kwargs['sms_refresh'] = '1' if sms_refresh else '0'
    if sms_message is not None:
        kwargs['sms_message'] = sms_message
    if fraud_email is not None:
        kwargs['fraud_email'] = fraud_email
    if keypress_confirm is not None:
        kwargs['keypress_confirm'] = keypress_confirm
    if keypress_fraud is not None:
        kwargs['keypress_fraud'] = keypress_fraud
    if timezone is not None:
        kwargs['timezone'] = timezone
    if caller_id is not None:
        kwargs['caller_id'] = caller_id

    if not kwargs:
        raise TypeError("No settings were provided")

    response = client.call_json_api(ikey, skey, host, 'POST', url, ca,
                                    **kwargs)
    return response


def get_info_summary(ikey, skey, host, ca=None):
    """
    Returns a summary of objects in the account.

    ikey - Admin API integration ikey
    skey - Admin API integration skey
    host - Duo host
    ca - Optional CA cert

    Raises RuntimeError on error.
    """
    response = client.call_json_api(
        ikey,
        skey,
        host,
        'GET',
        '/admin/v1/info/summary',
        ca,
    )
    return response


def get_info_telephony_credits_used(ikey, skey, host,
                                    mintime=None,
                                    maxtime=None,
                                    ca=None):
    """
    Returns number of telephony credits used during the time period.

    ikey - Admin API integration ikey
    skey - Admin API integration skey
    host - Duo host
    ca - Optional CA cert
    mintime - Limit report to data for events after this UNIX
              timestamp. Defaults to thirty days ago.
    maxtime - Limit report to data for events before this UNIX
              timestamp. Defaults to the current time.

    Raises RuntimeError on error.
    """
    response = client.call_json_api(
        ikey,
        skey,
        host,
        'GET',
        '/admin/v1/info/telephony_credits_used',
        ca,
    )
    return response


def get_authentication_attempts(ikey, skey, host,
                                mintime=None,
                                maxtime=None,
                                ca=None):
    """
    Returns counts of authentication attempts, broken down by result.

    ikey - Admin API integration ikey
    skey - Admin API integration skey
    host - Duo host
    ca - Optional CA cert
    mintime - Limit report to data for events after this UNIX
              timestamp. Defaults to thirty days ago.
    maxtime - Limit report to data for events before this UNIX
              timestamp. Defaults to the current time.

    Returns: {
        "ERROR": <int>,
        "FAILURE": <int>,
        "FRAUD": <int>,
        "SUCCESS": <int>
    }

    where each integer is the number of authentication attempts with
    that result.

    Raises RuntimeError on error.
    """
    response = client.call_json_api(
        ikey,
        skey,
        host,
        'GET',
        '/admin/v1/info/authentication_attempts',
        ca,
    )
    return response


def get_user_authentication_attempts(ikey, skey, host,
                                     mintime=None,
                                     maxtime=None,
                                     ca=None):
    """
    Returns number of unique users with each possible authentication result.

    ikey - Admin API integration ikey
    skey - Admin API integration skey
    host - Duo host
    ca - Optional CA cert
    mintime - Limit report to data for events after this UNIX
              timestamp. Defaults to thirty days ago.
    maxtime - Limit report to data for events before this UNIX
              timestamp. Defaults to the current time.

    Returns: {
        "ERROR": <int>,
        "FAILURE": <int>,
        "FRAUD": <int>,
        "SUCCESS": <int>
    }

    where each integer is the number of users who had at least one
    authentication attempt ending with that result. (These counts are
    thus always less than or equal to those returned by
    get_authentication_attempts.)

    Raises RuntimeError on error.
    """
    response = client.call_json_api(
        ikey,
        skey,
        host,
        'GET',
        '/admin/v1/info/user_authentication_attempts',
        ca,
    )
    return response


def get_integrations(ikey, skey, host, ca=None):
    """
    Returns list of integrations.

    ikey - Admin API integration ikey
    skey - Admin API integration skey
    host - Duo host
    ca - Optional CA cert

    Returns list of integration objects.

    Raises RuntimeError on error.
    """
    response = client.call_json_api(
        ikey,
        skey,
        host,
        'GET',
        '/admin/v1/integrations',
        ca,
    )
    return response


def get_integration(ikey, skey, host, integration_key, ca=None):
    """
    Returns the requested integration.

    ikey - Admin API integration ikey
    skey - Admin API integration skey
    host - Duo host
    integration_key - The ikey of the integration to get
    ca - Optional CA cert

    Returns list of integration objects.

    Raises RuntimeError on error.
    """
    response = client.call_json_api(
        ikey,
        skey,
        host,
        'GET',
        '/admin/v1/integrations/%s' % integration_key,
        ca,
    )
    return response


def create_integration(ikey, skey, host,
                       name,
                       integration_type,
                       visual_style=None,
                       greeting=None,
                       notes=None,
                       enroll_policy=None,
                       adminapi_admins=None,
                       adminapi_info=None,
                       adminapi_integrations=None,
                       adminapi_read_log=None,
                       adminapi_read_resource=None,
                       adminapi_settings=None,
                       adminapi_write_resource=None,
                       ca=None):
    """Creates a new integration.

    ikey - Admin API integration ikey
    skey - Admin API integration skey
    host - Duo host
    ca - Optional CA cert
    name - The name of the integration (required)
    integration_type - <str: integration type constant> (required)
                       See adminapi docs for possible values.
    visual_style - <str:visual style constant> (optional, default 'default')
                   See adminapi docs for possible values.
    greeting - <str:Voice greeting> (optional, default '')
    notes - <str:internal use> (optional, uses default setting)
    enroll_policy - <str:'enroll'|'allow'|'deny'> (optional, default 'enroll')
    adminapi_admins - <bool: admins permission>|None
    adminapi_info - <bool: info permission>|None
    adminapi_integrations - <bool:integrations permission>|None
    adminapi_read_log - <bool:read log permission>|None
    adminapi_read_resource - <bool: read resource permission>|None
    adminapi_settings - <bool: settings permission>|None
    adminapi_write_resource - <bool:write resource permission>|None

    Returns the created integration.

    Raises RuntimeError on error.

    """
    url = '/admin/v1/integrations'
    kwargs = {}
    if name is not None:
        kwargs['name'] = name
    if integration_type is not None:
        kwargs['type'] = integration_type
    if visual_style is not None:
        kwargs['visual_style'] = visual_style
    if greeting is not None:
        kwargs['greeting'] = greeting
    if notes is not None:
        kwargs['notes'] = notes
    if enroll_policy is not None:
        kwargs['enroll_policy'] = enroll_policy
    if adminapi_admins is not None:
        kwargs['adminapi_admins'] = '1' if adminapi_admins else '0'
    if adminapi_info is not None:
        kwargs['adminapi_info'] = '1' if adminapi_info else '0'
    if adminapi_integrations is not None:
        kwargs['adminapi_integrations'] = '1' if adminapi_integrations else '0'
    if adminapi_read_log is not None:
        kwargs['adminapi_read_log'] = '1' if adminapi_read_log else '0'
    if adminapi_read_resource is not None:
        kwargs['adminapi_read_resource'] = (
            '1' if adminapi_read_resource else '0')
    if adminapi_settings is not None:
        kwargs['adminapi_settings'] = '1' if adminapi_settings else '0'
    if adminapi_write_resource is not None:
        kwargs['adminapi_write_resource'] = (
            '1' if adminapi_write_resource else '0')
    response = client.call_json_api(ikey, skey, host, 'POST', url, ca,
                                    **kwargs)
    return response


def delete_integration(ikey, skey, host, integration_key, ca=None):
    """Deletes an integration.

    ikey - Admin API integration ikey
    skey - Admin API integration skey
    host - Duo host
    ca - Optional CA cert
    integration_key - The integration key of the integration to delete.

    Returns None.

    Raises RuntimeError on error.

    """
    url = '/admin/v1/integrations/%s' % integration_key

    client.call_json_api(ikey, skey, host, 'DELETE', url, ca)
    return None


def update_integration(ikey, skey, host,
                       integration_key,
                       name=None,
                       integration_type=None,
                       visual_style=None,
                       greeting=None,
                       notes=None,
                       enroll_policy=None,
                       adminapi_admins=None,
                       adminapi_info=None,
                       adminapi_integrations=None,
                       adminapi_read_log=None,
                       adminapi_read_resource=None,
                       adminapi_settings=None,
                       adminapi_write_resource=None,
                       reset_secret_key=None,
                       ca=None):
    """Updates an integration.

    ikey - Admin API integration ikey
    skey - Admin API integration skey
    host - Duo host
    ca - Optional CA cert
    integration_key - The key of the integration to update. (required)
    name - The name of the integration (optional)
    visual_style - (optional, default 'default')
                   See adminapi docs for possible values.
    greeting - Voice greeting (optional, default '')
    notes - internal use (optional, uses default setting)
    enroll_policy - <'enroll'|'allow'|'deny'> (optional, default 'enroll')
    adminapi_admins - <int:0|1>|None
    adminapi_info - True|False|None
    adminapi_integrations - True|False|None
    adminapi_read_log - True|False|None
    adminapi_read_resource - True|False|None
    adminapi_settings - True|False|None
    adminapi_write_resource - True|False|None
    reset_secret_key - <any value>|None

    If any value other than None is provided for 'reset_secret_key'
    (for example, 1), then a new secret key will be generated for the
    integration.

    Returns the created integration.

    Raises RuntimeError on error.

    """
    url = '/admin/v1/integrations/%s' % integration_key
    kwargs = {}
    if name is not None:
        kwargs['name'] = name
    if visual_style is not None:
        kwargs['visual_style'] = visual_style
    if greeting is not None:
        kwargs['greeting'] = greeting
    if notes is not None:
        kwargs['notes'] = notes
    if enroll_policy is not None:
        kwargs['enroll_policy'] = enroll_policy
    if adminapi_admins is not None:
        kwargs['adminapi_admins'] = '1' if adminapi_admins else '0'
    if adminapi_info is not None:
        kwargs['adminapi_info'] = '1' if adminapi_info else '0'
    if adminapi_integrations is not None:
        kwargs['adminapi_integrations'] = '1' if adminapi_integrations else '0'
    if adminapi_read_log is not None:
        kwargs['adminapi_read_log'] = '1' if adminapi_read_log else '0'
    if adminapi_read_resource is not None:
        kwargs['adminapi_read_resource'] = (
            '1' if adminapi_read_resource else '0')
    if adminapi_settings is not None:
        kwargs['adminapi_settings'] = '1' if adminapi_settings else '0'
    if adminapi_write_resource is not None:
        kwargs['adminapi_write_resource'] = (
            '1' if adminapi_write_resource else '0')
    if reset_secret_key is not None:
        kwargs['reset_secret_key'] = '1'

    if not kwargs:
        raise TypeError("No new values were provided")

    response = client.call_json_api(ikey, skey, host, 'POST', url, ca,
                                    **kwargs)
    return response


def get_admins(ikey, skey, host, ca=None):
    """
    Returns list of administrators.

    ikey - Admin API integration ikey
    skey - Admin API integration skey
    host - Duo host
    ca - Optional CA cert

    Returns list of administrator objects.  See the adminapi docs.

    Raises RuntimeError on error.
    """

    url = '/admin/v1/admins'
    response = client.call_json_api(
        ikey, skey, host, 'GET', url, ca)
    return response


def get_admin(ikey, skey, host, admin_id, ca=None):
    """
    Returns an administrator.

    ikey - Admin API integration ikey
    skey - Admin API integration skey
    host - Duo host
    ca - Optional CA cert
    admin_id - The id of the administrator.

    Returns an administrator.  See the adminapi docs.

    Raises RuntimeError on error.
    """

    url = '/admin/v1/admins/%s' % admin_id
    response = client.call_json_api(
        ikey, skey, host, 'GET', url, ca)
    return response


def add_admin(ikey, skey, host, name, email, phone, password, ca=None):
    """
    Create an administrator and adds it to a customer.

    ikey - Admin API integration ikey
    skey - Admin API integration skey
    host - Duo host
    ca - Optional CA cert
    name - <str:the name of the administrator>
    email - <str:email address>
    phone - <str:phone number>
    password - <str:pasword>

    Returns the added administrator.  See the adminapi docs.

    Raises RuntimeError on error.
    """

    url = '/admin/v1/admins'
    kwargs = {}
    if name is not None:
        kwargs['name'] = name
    if email is not None:
        kwargs['email'] = email
    if phone is not None:
        kwargs['phone'] = phone
    if password is not None:
        kwargs['password'] = phone

    response = client.call_json_api(
        ikey, skey, host, 'POST', url, ca, **kwargs)
    return response


def update_admin(ikey, skey, host, admin_id, name=None,
                 phone=None, password=None, ca=None):
    """
    Create an administrator and adds it to a customer.

    ikey - Admin API integration ikey
    skey - Admin API integration skey
    host - Duo host
    ca - Optional CA cert
    admin_id - The id of the administrator.
    name - <str:the name of the administrator> (optional)
    phone - <str:phone number> (optional)
    password - <str:password> (optional)

    Returns the updated administrator.  See the adminapi docs.

    Raises RuntimeError on error.
    """

    url = '/admin/v1/admins/%s' % admin_id
    kwargs = {}
    if name is not None:
        kwargs['name'] = name
    if phone is not None:
        kwargs['phone'] = phone
    if password is not None:
        kwargs['password'] = password

    response = client.call_json_api(
        ikey, skey, host, 'POST', url, ca, **kwargs)
    return response


def delete_admin(ikey, skey, host, admin_id, ca=None):
    """
    Deletes an administrator.

    ikey - Admin API integration ikey
    skey - Admin API integration skey
    host - Duo host
    ca - Optional CA cert
    admin_id - The id of the administrator.

    Returns None.

    Raises RuntimeError on error.
    """

    url = '/admin/v1/admins/%s' % admin_id
    client.call_json_api(ikey, skey, host, 'DELETE', url, ca)


def reset_admin(ikey, skey, host, admin_id, ca=None):
    """
    Resets the admin lockout.

    ikey - Admin API integration ikey
    skey - Admin API integration skey
    host - Duo host
    ca - Optional CA cert
    admin_id - <int:admin id>

    Returns None.

    Raises RuntimeError on error.
    """

    url = '/admin/v1/admins/%s/reset' % admin_id
    client.call_json_api(ikey, skey, host, 'POST', url, ca)


def activate_admin(ikey, skey, host, email, send_email=False,
                   valid_days=None, ca=None):
    """
    Generates an activate code for an administrator and optionally
    emails the administrator.

    ikey - Admin API integration ikey
    skey - Admin API integration skey
    host - Duo host
    ca - Optional CA cert
    email - <str:email address of administrator>
    valid_days - <int:number of days> (optional)
    send_email - <bool: True if email should be sent> (optional)

    Returns {
        "email": <str:email for admin/message>,
        "valid_days": <int:valid days>
        "link": <str:activation link>
        "message": <str:message, whether sent or not>
        "email_sent": <bool:true if email was sent, false otherwise>
        "code": <str:activation code>
    }

    See the adminapi docs for updated return values.

    Raises RuntimeError on error.
    """

    url = '/admin/v1/admins/activate'
    kwargs = {}
    if email is not None:
        kwargs['email'] = email
    if send_email is not None:
        kwargs['send_email'] = '1' if send_email else '0'
    if valid_days is not None:
        kwargs['valid_days'] = str(valid_days)
    response = client.call_json_api(ikey, skey, host, 'POST', url, ca, **kwargs)
    return response
