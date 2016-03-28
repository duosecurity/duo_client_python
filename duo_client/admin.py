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
         "last_login": <int:unix timestamp>|None,
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


DESKTOP_TOKENS

Desktop token objects are returned in the following format:

    {"desktoptoken_id": <str:phone id>,
     "name": <str>,
     "platform": <str:phone platform>|"Unknown",
     "type"": "Desktop Token",
     "users": [<user object>, ...]}

TOKENS

Token objects are returned in the following format:

    {"type": <str:token type>,
     "serial": <str:token serial number>,
     "token_id": <str:token id>,
     "totp_step": <int:number of seconds> or null,
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
     'lockout_expire_duration': <int:minutes until expiration>|0,
     'sms_expiration': <int:minutes until expiration>|0,
     'log_retention_days': <int:days to retain>|0,
     'sms_refresh': <bool:is sms refresh enabled (0|1)>,
     'telephony_warning_min': <int:credits>',
     'minimum_password_length': <int:minimum length>,
     'password_requires_upper_alpha': <bool:is upper alpha character required>,
     'password_requires_lower_alpha': <bool:is lower alpha character required>,
     'password_requires_numeric': <bool:is numeric character required>,
     'password_requires_special': <bool:is special character required>,
    }


INTEGRATIONS

Integration objects are returned in the following format:

    {'adminapi_admins': <bool:admins permission (0|1)>,
     'adminapi_info': <bool:info permission (0|1)>,
     'adminapi_integrations': <bool:integrations permission (0|1)>,
     'adminapi_read_log': <bool:read log permission (0|1)>,
     'adminapi_read_resource': <bool:read resource permission (0|1)>,
     'adminapi_settings': <bool:settings permission (0|1)>,
     'adminapi_write_resource': <bool:write resource permission (0|1)>,
     'self_service_allowed': <bool:self service permission (0|1)>,
     'enroll_policy': <str:enroll policy (enroll|allow|deny)>,
     'username_normalization_policy': <str:normalization policy (simple|none)>,
     'greeting': <str:voice greeting>,
     'integration_key': <str:integration key>,
     'name': <str:integration name>,
     'notes': <str:notes>,
     'secret_key': <str:secret key>,
     'type': <str:integration type>,
     'visual_style': <str:visual style>}

See the adminapi docs for possible values for enroll_policy, visual_style, ip_whitelist,
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
from __future__ import absolute_import

import six.moves.urllib

from . import client
import six

USER_STATUS_ACTIVE = 'active'
USER_STATUS_BYPASS = 'bypass'
USER_STATUS_DISABLED = 'disabled'
USER_STATUS_LOCKED_OUT = 'locked out'

TOKEN_HOTP_6 = 'h6'
TOKEN_HOTP_8 = 'h8'
TOKEN_YUBIKEY = 'yk'


class Admin(client.Client):
    account_id = None

    def api_call(self, method, path, params):
        if self.account_id is not None:
            params['account_id'] = self.account_id
        return super(Admin, self).api_call(method, path, params)

    @classmethod
    def _canonicalize_ip_whitelist(klass, ip_whitelist):
        if isinstance(ip_whitelist, six.string_types):
            return ip_whitelist
        else:
            return ','.join(ip_whitelist)
        pass

    @staticmethod
    def _canonicalize_bypass_codes(codes):
        if isinstance(codes, six.string_types):
            return codes
        else:
            return ','.join([str(int(code)) for code in codes])

    def get_administrator_log(self,
                              mintime=0):
        """
        Returns administrator log events.

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
        params = {
            'mintime': mintime,
        }
        response = self.json_api_call(
            'GET',
            '/admin/v1/logs/administrator',
            params,
        )
        for row in response:
            row['eventtype'] = 'administrator'
            row['host'] = self.host
        return response


    def get_authentication_log(self,
                               mintime=0):
        """
        Returns authentication log events.

        mintime - Fetch events only >= mintime (to avoid duplicate
                  records that have already been fetched)

        Returns:
            [
                {'timestamp': <int:unix timestamp>,
                 'eventtype': "authentication",
                 'host': <str:host>,
                 'device': <str:device>,
                 'username': <str:username>,
                 'factor': <str:factor>,
                 'result': <str:result>,
                 'ip': <str:ip address>,
                 'new_enrollment': <bool:if event corresponds to enrollment>,
                 'integration': <str:integration>}, ...
            ]

        Raises RuntimeError on error.
        """
        # Sanity check mintime as unix timestamp, then transform to string
        mintime = str(int(mintime))
        params = {
            'mintime': mintime,
        }
        response = self.json_api_call(
            'GET',
            '/admin/v1/logs/authentication',
            params,
        )
        for row in response:
            row['eventtype'] = 'authentication'
            row['host'] = self.host
        return response


    def get_telephony_log(self,
                          mintime=0):
        """
        Returns telephony log events.

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
        params = {
            'mintime': mintime,
        }
        response = self.json_api_call(
            'GET',
            '/admin/v1/logs/telephony',
            params,
        )
        for row in response:
            row['eventtype'] = 'telephony'
            row['host'] = self.host
        return response


    def get_users(self):
        """
        Returns list of users.


        Returns list of user objects.

        Raises RuntimeError on error.
        """
        response = self.json_api_call('GET', '/admin/v1/users', {})
        return response


    def get_user_by_id(self, user_id):
        """
        Returns user specified by user_id.

        user_id - User to fetch

        Returns user object.

        Raises RuntimeError on error.
        """
        user_id = six.moves.urllib.parse.quote_plus(str(user_id))
        path = '/admin/v1/users/' + user_id
        response = self.json_api_call('GET', path, {})
        return response


    def get_users_by_name(self, username):
        """
        Returns user specified by username.

        username - User to fetch

        Returns a list of 0 or 1 user objects.

        Raises RuntimeError on error.
        """
        params = {
            'username': username,
        }
        response = self.json_api_call('GET',
                                      '/admin/v1/users',
                                      params)
        return response


    def add_user(self, username, realname=None, status=None,
                 notes=None, email=None):
        """
        Adds a user.

        username - Username
        realname - User's real name (optional)
        status - User's status, defaults to USER_STATUS_ACTIVE
        notes - Comment field (optional)
        email - Email address (optional)

        Returns newly created user object.

        Raises RuntimeError on error.
        """
        params = {
            'username': username,
        }
        if realname is not None:
            params['realname'] = realname
        if status is not None:
            params['status'] = status
        if notes is not None:
            params['notes'] = notes
        if email is not None:
            params['email'] = email
        response = self.json_api_call('POST',
                                      '/admin/v1/users',
                                      params)
        return response


    def update_user(self, user_id, username=None, realname=None,
                    status=None, notes=None, email=None):
        """
        Update username, realname, status, or notes for a user.

        user_id - User ID
        username - Username (optional)
        realname - User's real name (optional)
        status - User's status, defaults to USER_STATUS_ACTIVE
        notes - Comment field (optional)
        email - Email address (optional)

        Returns updated user object.

        Raises RuntimeError on error.
        """
        user_id = six.moves.urllib.parse.quote_plus(str(user_id))
        path = '/admin/v1/users/' + user_id
        params = {}
        if username is not None:
            params['username'] = username
        if realname is not None:
            params['realname'] = realname
        if status is not None:
            params['status'] = status
        if notes is not None:
            params['notes'] = notes
        if email is not None:
            params['email'] = email
        response = self.json_api_call('POST', path, params)
        return response


    def delete_user(self, user_id):
        """
        Deletes a user. If the user is already deleted, does nothing.

        user_id - User ID

        Raises RuntimeError on error.
        """
        user_id = six.moves.urllib.parse.quote_plus(str(user_id))
        path = '/admin/v1/users/' + user_id
        return self.json_api_call('DELETE', path, {})

    def enroll_user(self, username, email, valid_secs=None):
        """
        Enroll a user and send them an enrollment email.

        username - Username
        email - Email address
        valid_secs - Seconds before the enrollment link expires
                     (if 0 it never expires)

        Returns nothing.

        Raises RuntimeError on error.
        """
        path = '/admin/v1/users/enroll'
        params = {
            'username': username,
            'email': email,
        }

        if valid_secs is not None:
            params['valid_secs'] = str(valid_secs)

        return self.json_api_call('POST', path, params)

    def get_user_bypass_codes(self, user_id, count=None, valid_secs=None, remaining_uses=None, codes=None):
        """
        Replace a user's bypass codes with new codes.

        user_id - User ID
        count - Number of new codes to randomly generate
        valid_secs - Seconds before codes expire (if 0 they will never expire)
        remaining_uses - The number of times this code can be used (0 is unlimited)
        codes - Optionally provide custom codes, otherwise will be random
        count and codes are mutually exclusive

        Returns a list of newly created codes.

        Raises RuntimeError on error.
        """
        user_id = six.moves.urllib.parse.quote_plus(str(user_id))
        path = '/admin/v1/users/' + user_id + '/bypass_codes'
        params = {}

        if count is not None:
            params['count'] = str(int(count))

        if valid_secs is not None:
            params['valid_secs'] = str(int(valid_secs))

        if remaining_uses is not None:
            params['reuse_count'] = str(int(remaining_uses))

        if codes is not None:
            params['codes'] = self._canonicalize_bypass_codes(codes)

        return self.json_api_call('POST', path, params)


    def get_user_phones(self, user_id):
        """
        Returns an array of phones associated with the user.

        user_id - User ID

        Returns list of phone objects.

        Raises RuntimeError on error.
        """
        user_id = six.moves.urllib.parse.quote_plus(str(user_id))
        path = '/admin/v1/users/' + user_id + '/phones'
        return self.json_api_call('GET', path, {})


    def add_user_phone(self, user_id, phone_id):
        """
        Associates a phone with a user.

        user_id - User ID
        phone_id - Phone ID

        Returns nothing.

        Raises RuntimeError on error.
        """
        user_id = six.moves.urllib.parse.quote_plus(str(user_id))
        path = '/admin/v1/users/' + user_id + '/phones'
        params = {
            'phone_id': phone_id,
        }
        return self.json_api_call('POST', path, params)


    def delete_user_phone(self, user_id, phone_id):
        """
        Dissociates a phone from a user.

        user_id - User ID
        phone_id - Phone ID

        Returns nothing.

        Raises RuntimeError on error.
        """
        user_id = six.moves.urllib.parse.quote_plus(str(user_id))
        path = '/admin/v1/users/' + user_id + '/phones/' + phone_id
        params = {}
        return self.json_api_call('DELETE', path,
                                    params)


    def get_user_tokens(self, user_id):
        """
        Returns an array of hardware tokens associated with the user.

        user_id - User ID

        Returns list of hardware token objects.

        Raises RuntimeError on error.
        """
        user_id = six.moves.urllib.parse.quote_plus(str(user_id))
        path = '/admin/v1/users/' + user_id + '/tokens'
        params = {}
        return self.json_api_call('GET', path,
                                    params)


    def add_user_token(self, user_id, token_id):
        """
        Associates a hardware token with a user.

        user_id - User ID
        token_id - Token ID

        Returns nothing.

        Raises RuntimeError on error.
        """
        user_id = six.moves.urllib.parse.quote_plus(str(user_id))
        path = '/admin/v1/users/' + user_id + '/tokens'
        params = {
            'token_id': token_id,
        }
        return self.json_api_call('POST', path, params)


    def delete_user_token(self, user_id, token_id):
        """
        Dissociates a hardware token from a user.

        user_id - User ID
        token_id - Hardware token ID

        Returns nothing.

        Raises RuntimeError on error.
        """
        user_id = six.moves.urllib.parse.quote_plus(str(user_id))
        token_id = six.moves.urllib.parse.quote_plus(str(token_id))
        path = '/admin/v1/users/' + user_id + '/tokens/' + token_id
        return self.json_api_call('DELETE', path, {})

    def get_user_groups(self, user_id):
        """
        Returns an array of groups associated with the user.

        user_id - User ID

        Returns list of groups objects.

        Raises RuntimeError on error.
        """
        user_id = six.moves.urllib.parse.quote_plus(str(user_id))
        path = '/admin/v1/users/' + user_id + '/groups'
        return self.json_api_call('GET', path, {})

    def add_user_group(self, user_id, group_id):
        """
        Associates a group with a user.

        user_id - User ID
        group_id - Group ID

        Returns nothing.

        Raises RuntimeError on error.
        """
        user_id = six.moves.urllib.parse.quote_plus(str(user_id))
        path = '/admin/v1/users/' + user_id + '/groups'
        params = {'group_id': group_id}
        return self.json_api_call('POST', path, params)

    def delete_user_group(self, user_id, group_id):
        """
        Dissociates a group from a user.

        user_id - User ID
        group_id - Group ID

        Returns nothing.

        Raises RuntimeError on error.
        """
        user_id = six.moves.urllib.parse.quote_plus(str(user_id))
        path = '/admin/v1/users/' + user_id + '/groups/' + group_id
        params = {}
        return self.json_api_call('DELETE', path, params)

    def get_phones(self):
        """
        Returns list of phones.


        Returns list of phone objects.

        Raises RuntimeError on error.
        """
        response = self.json_api_call('GET', '/admin/v1/phones', {})
        return response


    def get_phone_by_id(self, phone_id):
        """
        Returns a phone specified by phone_id.

        phone_id - Phone ID

        Returns phone object.

        Raises RuntimeError on error.
        """
        path = '/admin/v1/phones/' + phone_id
        response = self.json_api_call('GET', path, {})
        return response


    def get_phones_by_number(self, number, extension=None):
        """
        Returns a phone specified by number and extension.

        number - Phone number
        extension - Phone number extension (optional)

        Returns list of 0 or 1 phone objects.

        Raises RuntimeError on error.
        """
        path = '/admin/v1/phones'
        params = {'number': number}
        if extension is not None:
            params['extension'] = extension
        response = self.json_api_call('GET', path,
                                        params)
        return response


    def add_phone(self,
                  number=None,
                  extension=None,
                  name=None,
                  type=None,
                  platform=None,
                  predelay=None,
                  postdelay=None):
        """
        Adds a phone.

        number - Phone number (optional).
        extension - Phone number extension (optional).
        name - Phone name (optional).
        type - The phone type (optional).
        platform - The phone platform (optional).
        predelay - Number of seconds to wait after the number picks up
                   before dialing the extension (optional).
        postdelay - Number of seconds to wait after the extension is
                    dialed before the speaking the prompt (optional).

        Returns phone object.

        Raises RuntimeError on error.
        """
        path = '/admin/v1/phones'
        params = {}
        if number is not None:
            params['number'] = number
        if extension is not None:
            params['extension'] = extension
        if name is not None:
            params['name'] = name
        if type is not None:
            params['type'] = type
        if platform is not None:
            params['platform'] = platform
        if predelay is not None:
            params['predelay'] = predelay
        if postdelay is not None:
            params['postdelay'] = postdelay
        response = self.json_api_call('POST', path,
                                        params)
        return response


    def update_phone(self, phone_id,
                     number=None,
                     extension=None,
                     name=None,
                     type=None,
                     platform=None,
                     predelay=None,
                     postdelay=None):
        """
        Update a phone.

        number - Phone number (optional)
        extension - Phone number extension (optional).
        name - Phone name (optional).
        type - The phone type (optional).
        platform - The phone platform (optional).
        predelay - Number of seconds to wait after the number picks up
                   before dialing the extension (optional).
        postdelay - Number of seconds to wait after the extension is
                    dialed before the speaking the prompt (optional).

        Returns phone object.

        Raises RuntimeError on error.
        """
        phone_id = six.moves.urllib.parse.quote_plus(str(phone_id))
        path = '/admin/v1/phones/' + phone_id
        params = {}
        if number is not None:
            params['number'] = number
        if extension is not None:
            params['extension'] = extension
        if name is not None:
            params['name'] = name
        if type is not None:
            params['type'] = type
        if platform is not None:
            params['platform'] = platform
        if predelay is not None:
            params['predelay'] = predelay
        if postdelay is not None:
            params['postdelay'] = postdelay
        response = self.json_api_call('POST', path,
                                        params)
        return response


    def delete_phone(self, phone_id):
        """
        Deletes a phone. If the phone has already been deleted, does nothing.

        phone_id - Phone ID.

        Raises RuntimeError on error.
        """
        path = '/admin/v1/phones/' + phone_id
        params = {}
        return self.json_api_call('DELETE', path, params)


    def send_sms_activation_to_phone(self, phone_id,
                                     valid_secs=None,
                                     install=None,
                                     installation_msg=None,
                                     activation_msg=None):
        """
        Generate a Duo Mobile activation code and send it to the phone via
        SMS, optionally sending an additional message with a PATH to
        install Duo Mobile.

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

        Returns: {
            "activation_barcode": "https://api-abcdef.duosecurity.com/frame/qr?value=duo%3A%2F%2Factivation-code",
            "activation_msg": "To activate the Duo Mobile app, click this link: https://m-abcdef.duosecurity.com/iphone/7dmi4Oowz5g3J47FARLs",
            "installation_msg": "Welcome to Duo! To install the Duo Mobile app, click this link: http://m-abcdef.duosecurity.com",
            "valid_secs": 3600
        }

        Raises RuntimeError on error.
        """
        path = '/admin/v1/phones/' + phone_id + '/send_sms_activation'
        params = {}
        if valid_secs is not None:
            params['valid_secs'] = str(valid_secs)
        if install is not None:
            params['install'] = str(int(bool(install)))
        if installation_msg is not None:
            params['installation_msg'] = installation_msg
        if activation_msg is not None:
            params['activation_msg'] = activation_msg
        return self.json_api_call('POST', path,
                                    params)

    def create_activation_url(self, phone_id,
                              valid_secs=None,
                              install=None):
        """
        Create an activation code for Duo Mobile.

        phone_id - Phone ID.
        valid_secs - The number of seconds activation code should be valid for.
                     Default: 86400 seconds (one day).
        install - '1' to also return an installation_url for Duo
                  Mobile; '0' to not return. Default: '0'.

        Returns: {
            "activation_barcode": "https://api-abcdef.duosecurity.com/frame/qr?value=duo%3A%2F%2Factivation-code",
            "activation_url": "https://m-abcdef.duosecurity.com/iphone/7dmi4Oowz5g3J47FARLs",
            "valid_secs": 3600
        }

        Raises RuntimeError on error.
        """
        path = '/admin/v1/phones/' + phone_id + '/activation_url'
        params = {}
        if valid_secs is not None:
            params['valid_secs'] = str(valid_secs)
        if install is not None:
            params['install'] = str(int(bool(install)))
        return self.json_api_call('POST', path, params)

    def send_sms_installation(self, phone_id,
                              installation_msg=None):
        """
        Send a message via SMS describing how to install Duo Mobile.

        phone_id - Phone ID.
        installation_msg - Custom installation message template to send to
                           the user if install was 1. Must contain
                           <insturl>, which is replaced with the
                           installation URL.

        Returns: {
            "installation_msg": "Welcome to Duo! To install the Duo Mobile app, click this link: http://m-abcdef.duosecurity.com",
        }

        Raises RuntimeError on error.
        """
        path = '/admin/v1/phones/' + phone_id + '/send_sms_installation'
        params = {}
        if installation_msg is not None:
            params['installation_msg'] = installation_msg
        return self.json_api_call('POST', path, params)

    def get_desktoptokens(self):
        """
        Returns list of desktop tokens.

        Returns list of desktop token objects.

        Raises RuntimeError on error.
        """
        response = self.json_api_call('GET', '/admin/v1/desktoptokens', {})
        return response

    def get_desktoptoken_by_id(self, desktoptoken_id):
        """
        Returns a desktop token specified by dtoken_id.

        desktoptoken_id - Desktop Token ID

        Returns desktop token object.

        Raises RuntimeError on error.
        """
        path = '/admin/v1/desktoptokens/' + desktoptoken_id
        response = self.json_api_call('GET', path, {})
        return response

    def add_desktoptoken(self,
                         platform,
                         name=None):
        """
        Adds a desktop token.

        Returns desktop token object.

        platform - The desktop token platform.
        name - Desktop token name (optional).

        Raises RuntimeError on error.
        """
        params = {
            'platform': platform,
        }
        if name is not None:
            params['name'] = name
        response = self.json_api_call('POST',
                                      '/admin/v1/desktoptokens',
                                      params)
        return response


    def delete_desktoptoken(self, desktoptoken_id):
        """
        Deletes a desktop token. If the desktop token has already been deleted,
        does nothing.

        desktoptoken_id - Desktop token ID.

        Returns nothing.

        Raises RuntimeError on error.
        """
        path = '/admin/v1/desktoptokens/' + six.moves.urllib.parse.quote_plus(desktoptoken_id)
        params = {}
        return self.json_api_call('DELETE', path, params)


    def update_desktoptoken(self,
                            desktoptoken_id,
                            platform=None,
                            name=None):
        """
        Update a desktop token.

        Returns desktop token object.

        name - Desktop token name (optional).
        platform - The desktop token platform (optional).

        Raises RuntimeError on error.
        """
        desktoptoken_id = six.moves.urllib.parse.quote_plus(str(desktoptoken_id))
        path = '/admin/v1/desktoptokens/' + desktoptoken_id
        params = {}
        if platform is not None:
            params['platform'] = platform
        if name is not None:
            params['name'] = name
        response = self.json_api_call('POST',
                                      path,
                                      params)
        return response


    def activate_desktoptoken(self, desktoptoken_id, valid_secs=None):
        """
        Generates an activation code for a desktop token.

        Returns activation info like:
        {
            'activation_msg': <str:message with activation url>,
            'activation_url': <str:activation url>,
            'valid_secs': <int:seconds>}

        Raises RuntimeError on error.
        """

        params = {}
        if valid_secs:
            params['valid_secs'] = str(valid_secs)
        quoted_id = six.moves.urllib.parse.quote_plus(desktoptoken_id)
        response = self.json_api_call('POST',
            '/admin/v1/desktoptokens/%s/activate' % quoted_id,
            params)
        return response


    def get_tokens(self):
        """
        Returns list of tokens.


        Returns list of token objects.
        """
        params = {}
        response = self.json_api_call(
            'GET', '/admin/v1/tokens',
            params
        )
        return response


    def get_token_by_id(self, token_id):
        """
        Returns a token.

        token_id - Token ID

        Returns a token object.
        """
        token_id = six.moves.urllib.parse.quote_plus(str(token_id))
        path = '/admin/v1/tokens/' + token_id
        params = {}
        response = self.json_api_call('GET', path,
                                        params)
        return response


    def get_tokens_by_serial(self, type, serial):
        """
        Returns a token.

        type - Token type, one of TOKEN_HOTP_6, TOKEN_HOTP_8, TOKEN_YUBIKEY
        serial - Token serial number

        Returns a list of 0 or 1 token objects.
        """
        params = {
            'type': type,
            'serial': serial,
        }
        response = self.json_api_call('GET', '/admin/v1/tokens', params)
        return response


    def delete_token(self, token_id):
        """
        Deletes a token. If the token is already deleted, does nothing.

        token_id - Token ID
        """
        token_id = six.moves.urllib.parse.quote_plus(str(token_id))
        path = '/admin/v1/tokens/' + token_id
        return self.json_api_call('DELETE', path, {})


    def add_hotp6_token(self, serial, secret, counter=None):
        """
        Add a HOTP6 token.

        serial - Token serial number
        secret - HOTP secret
        counter - Initial counter value (default: 0)

        Returns newly added token object.
        """
        path = '/admin/v1/tokens'
        params = {'type': 'h6', 'serial': serial, 'secret': secret}
        if counter is not None:
            params['counter'] = str(int(counter))
        response = self.json_api_call('POST', path,
                                        params)
        return response


    def add_hotp8_token(self, serial, secret, counter=None):
        """
        Add a HOTP8 token.

        serial - Token serial number
        secret - HOTP secret
        counter - Initial counter value (default: 0)

        Returns newly added token object.
        """
        path = '/admin/v1/tokens'
        params = {'type': 'h8', 'serial': serial, 'secret': secret}
        if counter is not None:
            params['counter'] = str(int(counter))
        response = self.json_api_call('POST', path,
                                        params)
        return response


    def add_totp6_token(self, serial, secret, totp_step=None):
        """
        Add a TOTP6 token.

        serial - Token serial number
        secret - TOTP secret
        totp_step - Time step (default: 30 seconds)

        Returns newly added token object.
        """
        path = '/admin/v1/tokens'
        params = {'type': 't6', 'serial': serial, 'secret': secret}
        if totp_step is not None:
            params['totp_step'] = str(int(totp_step))
        response = self.json_api_call('POST', path,
                                        params)
        return response


    def add_totp8_token(self, serial, secret, totp_step=None):
        """
        Add a TOTP8 token.

        serial - Token serial number
        secret - TOTP secret
        totp_step - Time step (default: 30 seconds)

        Returns newly added token object.
        """
        path = '/admin/v1/tokens'
        params = {'type': 't8', 'serial': serial, 'secret': secret}
        if totp_step is not None:
            params['totp_step'] = str(int(totp_step))
        response = self.json_api_call('POST', path,
                                        params)
        return response

    def update_token(self, token_id, totp_step=None):
        """
        Update a token.

        totp_step - Time step (optional)

        Returns token object.

        Raises RuntimeError on error.
        """
        token_id = six.moves.urllib.parse.quote_plus(str(token_id))
        path = '/admin/v1/tokens/' + token_id
        params = {}
        if totp_step is not None:
            params['totp_step'] = totp_step
        response = self.json_api_call('POST', path,
                                        params)
        return response


    def add_yubikey_token(self, serial, private_id, aes_key):
        """
        Add a Yubikey AES token.

        serial - Token serial number
        secret - HOTP secret

        Returns newly added token object.
        """
        path = '/admin/v1/tokens'
        params = {'type': 'yk', 'serial': serial, 'private_id': private_id,
                  'aes_key': aes_key}
        response = self.json_api_call('POST', path,
                                        params)
        return response


    def resync_hotp_token(self, token_id, code1, code2, code3):
        """
        Resync HOTP counter. The user must generate 3 consecutive OTP
        from their token and input them as code1, code2, and code3. This
        function will scan ahead in the OTP sequence to find a counter
        that resyncs with those 3 codes.

        token_id - Token ID
        code1 - First OTP from token
        code2 - Second OTP from token
        code3 - Third OTP from token

        Returns nothing on success.
        """
        token_id = six.moves.urllib.parse.quote_plus(str(token_id))
        path = '/admin/v1/tokens/' + token_id + '/resync'
        params = {'code1': code1, 'code2': code2, 'code3': code3}
        return self.json_api_call('POST', path, params)

    def get_settings(self):
        """
        Returns customer settings.

        Returns a settings object.

        Raises RuntimeError on error.
        """
        return self.json_api_call('GET', '/admin/v1/settings', {})

    def update_settings(self,
                        lockout_threshold=None,
                        lockout_expire_duration=None,
                        inactive_user_expiration=None,
                        log_retention_days=None,
                        sms_batch=None,
                        sms_expiration=None,
                        sms_refresh=None,
                        sms_message=None,
                        fraud_email=None,
                        fraud_email_enabled=None,
                        keypress_confirm=None,
                        keypress_fraud=None,
                        timezone=None,
                        telephony_warning_min=None,
                        caller_id=None,
                        push_enabled=None,
                        voice_enabled=None,
                        sms_enabled=None,
                        mobile_otp_enabled=None,
                        u2f_enabled=None,
                        user_telephony_cost_max=None,
                        minimum_password_length=None,
                        password_requires_upper_alpha=None,
                        password_requires_lower_alpha=None,
                        password_requires_numeric=None,
                        password_requires_special=None):
        """
        Update settings.

        lockout_threshold - <int:number of attempts>|None
        lockout_expire_duration - <int:minutes>|0|None
        inactive_user_expiration - <int:number of days>|None
        log_retention_days - <int:number of days>|0|None
        sms_batch - <int:batch size>|None
        sms_expiration - <int:minutes>|None
        sms_refresh - True|False|None
        sms_message - <str:message>|None
        fraud_email - <str:email address>|None
        fraud_email_enabled - True|False|None
        keypress_confirm - <str:0-9, #, or *>|None
        keypress_fraud - <str:0-9, #, or *>|None
        timezone - <str:IANA timezone>|None
        telephony_warning_min - <int:credits>
        caller_id - <str:phone number>
        push_enabled - True|False|None
        sms_enabled = True|False|None
        voice_enabled = True|False|None
        mobile_otp_enabled = True|False|None
        u2f_enabled = True|False|None
        user_telephony_cost_max = <int:positive number of credits>
        minimum_password_length = <int:length>|None,
        password_requires_upper_alpha = True|False|None
        password_requires_lower_alpha = True|False|None
        password_requires_numeric = True|False|None
        password_requires_special = True|False|None

        Returns updated settings object.

        Raises RuntimeError on error.

        """
        params = {}
        if lockout_threshold is not None:
            params['lockout_threshold'] = str(lockout_threshold)
        if lockout_expire_duration is not None:
            params['lockout_expire_duration'] = str(lockout_expire_duration)
        if inactive_user_expiration is not None:
            params['inactive_user_expiration'] = str(inactive_user_expiration)
        if log_retention_days is not None:
            params['log_retention_days'] = str(log_retention_days)
        if sms_batch is not None:
            params['sms_batch'] = str(sms_batch)
        if sms_expiration is not None:
            params['sms_expiration'] = str(sms_expiration)
        if sms_refresh is not None:
            params['sms_refresh'] = '1' if sms_refresh else '0'
        if sms_message is not None:
            params['sms_message'] = sms_message
        if fraud_email is not None:
            params['fraud_email'] = fraud_email
        if fraud_email_enabled is not None:
            params['fraud_email_enabled'] = fraud_email_enabled
        if keypress_confirm is not None:
            params['keypress_confirm'] = keypress_confirm
        if keypress_fraud is not None:
            params['keypress_fraud'] = keypress_fraud
        if timezone is not None:
            params['timezone'] = timezone
        if telephony_warning_min is not None:
            params['telephony_warning_min'] = str(telephony_warning_min)
        if caller_id is not None:
            params['caller_id'] = caller_id
        if push_enabled is not None:
            params['push_enabled'] = '1' if push_enabled else '0'
        if sms_enabled is not None:
            params['sms_enabled'] = '1' if sms_enabled else '0'
        if voice_enabled is not None:
            params['voice_enabled'] = '1' if voice_enabled else '0'
        if mobile_otp_enabled is not None:
            params['mobile_otp_enabled'] = '1' if mobile_otp_enabled else '0'
        if u2f_enabled is not None:
            params['u2f_enabled'] = '1' if u2f_enabled else '0'
        if user_telephony_cost_max is not None:
            params['user_telephony_cost_max'] = str(user_telephony_cost_max)
        if minimum_password_length is not None:
            params['minimum_password_length'] = str(minimum_password_length)
        if password_requires_upper_alpha is not None:
            params['password_requires_upper_alpha'] = ('1' if
              password_requires_upper_alpha else '0')
        if password_requires_lower_alpha is not None:
            params['password_requires_lower_alpha'] = ('1' if
              password_requires_lower_alpha else '0')
        if password_requires_numeric is not None:
            params['password_requires_numeric'] = ('1' if
              password_requires_numeric else '0')
        if password_requires_special is not None:
            params['password_requires_special'] = ('1' if
              password_requires_special else '0')

        if not params:
            raise TypeError("No settings were provided")

        response = self.json_api_call('POST',
                                      '/admin/v1/settings',
                                      params)
        return response


    def get_info_summary(self):
        """
        Returns a summary of objects in the account.


        Raises RuntimeError on error.
        """
        params = {}
        response = self.json_api_call(
            'GET',
            '/admin/v1/info/summary',
            params
        )
        return response


    def get_info_telephony_credits_used(self,
                                        mintime=None,
                                        maxtime=None):
        """
        Returns number of telephony credits used during the time period.

        mintime - Limit report to data for events after this UNIX
                  timestamp. Defaults to thirty days ago.
        maxtime - Limit report to data for events before this UNIX
                  timestamp. Defaults to the current time.

        Raises RuntimeError on error.
        """
        params = {}
        if mintime is not None:
            params['mintime'] = mintime
        if maxtime is not None:
            params['maxtime'] = maxtime
        response = self.json_api_call(
            'GET',
            '/admin/v1/info/telephony_credits_used',
            params
        )
        return response


    def get_authentication_attempts(self,
                                    mintime=None,
                                    maxtime=None):
        """
        Returns counts of authentication attempts, broken down by result.

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
        params = {}
        if mintime is not None:
            params['mintime'] = mintime
        if maxtime is not None:
            params['maxtime'] = maxtime
        response = self.json_api_call(
            'GET',
            '/admin/v1/info/authentication_attempts',
            params
        )
        return response


    def get_user_authentication_attempts(self,
                                         mintime=None,
                                         maxtime=None):
        """
        Returns number of unique users with each possible authentication result.

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
        params = {}
        if mintime is not None:
            params['mintime'] = mintime
        if maxtime is not None:
            params['maxtime'] = maxtime
        response = self.json_api_call(
            'GET',
            '/admin/v1/info/user_authentication_attempts',
            params
        )
        return response

    def get_groups(self):
        """
        Returns a list of groups.
        """
        return self.json_api_call(
            'GET',
            '/admin/v1/groups',
            {}
        )

    def get_group(self, gkey):
        """
        Returns a group by gkey.
        """
        return self.json_api_call(
            'GET',
            '/admin/v1/groups/' + gkey,
            {}
        )

    def create_group(self, name,
                    desc=None,
                    status=None,
                    push_enabled=None,
                    sms_enabled=None,
                    voice_enabled=None,
                    mobile_otp_enabled=None,
                    u2f_enabled=None,
    ):
        """
        Create a new group.

        name - The name of the group (Required)
        desc - Group description (Optional)
        status - Group authentication status <str: 'active'/'disabled'/'bypass'> (Optional)
        push_enabled - Push factor restriction <True/False> (Optional)
        sms_enabled - SMS factor restriction <True/False> (Optional)
        voice_enabled - Voice factor restriction <True/False> (Optional)
        mobile_otp_enabled - Mobile OTP restriction <>True/False (Optional)
        """
        params = {
            'name': name,
        }
        if desc is not None:
            params['desc'] = desc
        if status is not None:
            params['status'] = status
        if push_enabled is not None:
            params['push_enabled'] = '1' if push_enabled else '0'
        if sms_enabled is not None:
            params['sms_enabled'] = '1' if sms_enabled else '0'
        if voice_enabled is not None:
            params['voice_enabled'] = '1' if voice_enabled else '0'
        if mobile_otp_enabled is not None:
            params['mobile_otp_enabled'] = '1' if mobile_otp_enabled else '0'
        if u2f_enabled is not None:
            params['u2f_enabled'] = '1' if u2f_enabled else '0'
        response = self.json_api_call(
            'POST',
            '/admin/v1/groups',
            params
        )
        return response

    def delete_group(self, gkey):
        """
        Delete a group by gkey
        """
        return self.json_api_call(
            'DELETE',
            '/admin/v1/groups/' + gkey,
            {}
        )

    def modify_group(self,
                     gkey,
                     name=None,
                     desc=None,
                     status=None,
                     push_enabled=None,
                     sms_enabled=None,
                     voice_enabled=None,
                     mobile_otp_enabled=None,
                     u2f_enabled=None,
    ):
        """
        Modify a group

        gkey - Group to modify (Required)
        name - New group name (Optional)
        desc - New group description (Optional)
        status - Group authentication status <str: 'active'/'disabled'/'bypass'> (Optional)
        push_enabled - Push factor restriction <True/False> (Optional)
        sms_enabled - SMS factor restriction <True/False> (Optional)
        voice_enabled - Voice factor restriction <True/False> (Optional)
        mobile_otp_enabled - Mobile OTP restriction <True/False> (Optional)
        u2f_enabled - u2f restriction <True/False> (Optional)
        """
        params = {}
        if name is not None:
            params['name'] = name
        if desc is not None:
            params['desc'] = desc
        if status is not None:
            params['status'] = status
        if push_enabled is not None:
            params['push_enabled'] = '1' if push_enabled else '0'
        if sms_enabled is not None:
            params['sms_enabled'] = '1' if sms_enabled else '0'
        if voice_enabled is not None:
            params['voice_enabled'] = '1' if voice_enabled else '0'
        if mobile_otp_enabled is not None:
            params['mobile_otp_enabled'] = '1' if mobile_otp_enabled else '0'
        if u2f_enabled is not None:
            params['u2f_enabled'] = '1' if u2f_enabled else '0'
        response = self.json_api_call(
            'POST',
            '/admin/v1/groups/' + gkey,
            params
        )
        return response


    def get_integrations(self):
        """
        Returns list of integrations.


        Returns list of integration objects.

        Raises RuntimeError on error.
        """
        params = {}
        response = self.json_api_call(
            'GET',
            '/admin/v1/integrations',
            params
        )
        return response


    def get_integration(self, integration_key):
        """
        Returns the requested integration.

        integration_key - The ikey of the integration to get

        Returns list of integration objects.

        Raises RuntimeError on error.
        """
        params = {}
        response = self.json_api_call(
            'GET',
            '/admin/v1/integrations/' + integration_key,
            params
        )
        return response


    def create_integration(self,
                           name,
                           integration_type,
                           visual_style=None,
                           greeting=None,
                           notes=None,
                           enroll_policy=None,
                           username_normalization_policy=None,
                           adminapi_admins=None,
                           adminapi_info=None,
                           adminapi_integrations=None,
                           adminapi_read_log=None,
                           adminapi_read_resource=None,
                           adminapi_settings=None,
                           adminapi_write_resource=None,
                           trusted_device_days=None,
                           ip_whitelist=None,
                           ip_whitelist_enroll_policy=None,
                           groups_allowed=None,
                           self_service_allowed=None):
        """Creates a new integration.

        name - The name of the integration (required)
        integration_type - <str: integration type constant> (required)
                           See adminapi docs for possible values.
        visual_style - <str:visual style constant> (optional, default 'default')
                       See adminapi docs for possible values.
        greeting - <str:Voice greeting> (optional, default '')
        notes - <str:internal use> (optional, uses default setting)
        enroll_policy - <str:'enroll'|'allow'|'deny'> (optional, default 'enroll')
        username_normalization_policy - <str:'simple'|'none'> (optional, default 'none')
        trusted_device_days - <int: days>|None
        ip_whitelist - <str: CSV list of IP/Ranges>|None
                       See adminapi docs for more details.
        ip_whitelist_enroll_policy - <bool: policy>
                                     See adminapi docs for more details.
        adminapi_admins - <bool: admins permission>|None
        adminapi_info - <bool: info permission>|None
        adminapi_integrations - <bool:integrations permission>|None
        adminapi_read_log - <bool:read log permission>|None
        adminapi_read_resource - <bool: read resource permission>|None
        adminapi_settings - <bool: settings permission>|None
        adminapi_write_resource - <bool:write resource permission>|None
        groups_allowed - <str: CSV list of gkeys of groups allowed to auth>
        self_service_allowed - <bool: self service permission>|None

        Returns the created integration.

        Raises RuntimeError on error.

        """
        params = {}
        if name is not None:
            params['name'] = name
        if integration_type is not None:
            params['type'] = integration_type
        if visual_style is not None:
            params['visual_style'] = visual_style
        if greeting is not None:
            params['greeting'] = greeting
        if notes is not None:
            params['notes'] = notes
        if username_normalization_policy is not None:
            params['username_normalization_policy'] = username_normalization_policy
        if enroll_policy is not None:
            params['enroll_policy'] = enroll_policy
        if trusted_device_days is not None:
            params['trusted_device_days'] = str(trusted_device_days)
        if ip_whitelist is not None:
            params['ip_whitelist'] = self._canonicalize_ip_whitelist(ip_whitelist)
        if ip_whitelist_enroll_policy is not None:
            params['ip_whitelist_enroll_policy'] = ip_whitelist_enroll_policy
        if adminapi_admins is not None:
            params['adminapi_admins'] = '1' if adminapi_admins else '0'
        if adminapi_info is not None:
            params['adminapi_info'] = '1' if adminapi_info else '0'
        if adminapi_integrations is not None:
            params['adminapi_integrations'] = '1' if adminapi_integrations else '0'
        if adminapi_read_log is not None:
            params['adminapi_read_log'] = '1' if adminapi_read_log else '0'
        if adminapi_read_resource is not None:
            params['adminapi_read_resource'] = (
                '1' if adminapi_read_resource else '0')
        if adminapi_settings is not None:
            params['adminapi_settings'] = '1' if adminapi_settings else '0'
        if adminapi_write_resource is not None:
            params['adminapi_write_resource'] = (
                '1' if adminapi_write_resource else '0')
        if groups_allowed is not None:
            params['groups_allowed'] = groups_allowed
        if self_service_allowed is not None:
            params['self_service_allowed'] = '1' if self_service_allowed else '0'
        response = self.json_api_call('POST',
                                      '/admin/v1/integrations',
                                      params)
        return response


    def delete_integration(self, integration_key):
        """Deletes an integration.

        integration_key - The integration key of the integration to delete.

        Raises RuntimeError on error.

        """
        integration_key = six.moves.urllib.parse.quote_plus(str(integration_key))
        path = '/admin/v1/integrations/%s' % integration_key
        return self.json_api_call('DELETE', path, {})


    def update_integration(self,
                           integration_key,
                           name=None,
                           visual_style=None,
                           greeting=None,
                           notes=None,
                           enroll_policy=None,
                           username_normalization_policy=None,
                           adminapi_admins=None,
                           adminapi_info=None,
                           adminapi_integrations=None,
                           adminapi_read_log=None,
                           adminapi_read_resource=None,
                           adminapi_settings=None,
                           adminapi_write_resource=None,
                           reset_secret_key=None,
                           trusted_device_days=None,
                           ip_whitelist=None,
                           ip_whitelist_enroll_policy=None,
                           groups_allowed=None,
                           self_service_allowed=None):
        """Updates an integration.

        integration_key - The key of the integration to update. (required)
        name - The name of the integration (optional)
        visual_style - (optional, default 'default')
                       See adminapi docs for possible values.
        greeting - Voice greeting (optional, default '')
        notes - internal use (optional, uses default setting)
        enroll_policy - <'enroll'|'allow'|'deny'> (optional, default 'enroll')
        trusted_device_days - <int: days>|None
        ip_whitelist - <str: CSV list of IP/Ranges>|None
                       See adminapi docs for more details.
        ip_whitelist_enroll_policy - <bool: policy>
                                     See adminapi docs for more details.
        adminapi_admins - <int:0|1>|None
        adminapi_info - True|False|None
        adminapi_integrations - True|False|None
        adminapi_read_log - True|False|None
        adminapi_read_resource - True|False|None
        adminapi_settings - True|False|None
        adminapi_write_resource - True|False|None
        reset_secret_key - <any value>|None
        groups_allowed - <str: CSV list of gkeys of groups allowed to auth>
        self_service_allowed - True|False|None

        If any value other than None is provided for 'reset_secret_key'
        (for example, 1), then a new secret key will be generated for the
        integration.

        Returns the created integration.

        Raises RuntimeError on error.

        """
        integration_key = six.moves.urllib.parse.quote_plus(str(integration_key))
        path = '/admin/v1/integrations/%s' % integration_key
        params = {}
        if name is not None:
            params['name'] = name
        if visual_style is not None:
            params['visual_style'] = visual_style
        if greeting is not None:
            params['greeting'] = greeting
        if notes is not None:
            params['notes'] = notes
        if enroll_policy is not None:
            params['enroll_policy'] = enroll_policy
        if username_normalization_policy is not None:
            params['username_normalization_policy'] = username_normalization_policy
        if trusted_device_days is not None:
            params['trusted_device_days'] = str(trusted_device_days)
        if ip_whitelist is not None:
            params['ip_whitelist'] = self._canonicalize_ip_whitelist(ip_whitelist)
        if ip_whitelist_enroll_policy is not None:
            params['ip_whitelist_enroll_policy'] = ip_whitelist_enroll_policy
        if adminapi_admins is not None:
            params['adminapi_admins'] = '1' if adminapi_admins else '0'
        if adminapi_info is not None:
            params['adminapi_info'] = '1' if adminapi_info else '0'
        if adminapi_integrations is not None:
            params['adminapi_integrations'] = '1' if adminapi_integrations else '0'
        if adminapi_read_log is not None:
            params['adminapi_read_log'] = '1' if adminapi_read_log else '0'
        if adminapi_read_resource is not None:
            params['adminapi_read_resource'] = (
                '1' if adminapi_read_resource else '0')
        if adminapi_settings is not None:
            params['adminapi_settings'] = '1' if adminapi_settings else '0'
        if adminapi_write_resource is not None:
            params['adminapi_write_resource'] = (
                '1' if adminapi_write_resource else '0')
        if reset_secret_key is not None:
            params['reset_secret_key'] = '1'
        if groups_allowed is not None:
            params['groups_allowed'] = groups_allowed
        if self_service_allowed is not None:
            params['self_service_allowed'] = '1' if self_service_allowed else '0'

        if not params:
            raise TypeError("No new values were provided")

        response = self.json_api_call('POST', path, params)
        return response


    def get_admins(self):
        """
        Returns list of administrators.


        Returns list of administrator objects.  See the adminapi docs.

        Raises RuntimeError on error.
        """
        response = self.json_api_call('GET', '/admin/v1/admins', {})
        return response


    def get_admin(self, admin_id):
        """
        Returns an administrator.

        admin_id - The id of the administrator.

        Returns an administrator.  See the adminapi docs.

        Raises RuntimeError on error.
        """
        admin_id = six.moves.urllib.parse.quote_plus(str(admin_id))
        path = '/admin/v1/admins/%s' % admin_id
        response = self.json_api_call('GET', path, {})
        return response


    def add_admin(self, name, email, phone, password, role=None):
        """
        Create an administrator and adds it to a customer.

        name - <str:the name of the administrator>
        email - <str:email address>
        phone - <str:phone number>
        password - <str:password>
        role - <str|None:role>

        Returns the added administrator.  See the adminapi docs.

        Raises RuntimeError on error.
        """
        params = {}
        if name is not None:
            params['name'] = name
        if email is not None:
            params['email'] = email
        if phone is not None:
            params['phone'] = phone
        if password is not None:
            params['password'] = password
        if role is not None:
            params['role'] = role
        response = self.json_api_call('POST', '/admin/v1/admins', params)
        return response


    def update_admin(self, admin_id,
                     name=None,
                     phone=None,
                     password=None):
        """
        Update one or more attributes of an administrator.

        admin_id - The id of the administrator.
        name - <str:the name of the administrator> (optional)
        phone - <str:phone number> (optional)
        password - <str:password> (optional)

        Returns the updated administrator.  See the adminapi docs.

        Raises RuntimeError on error.
        """
        admin_id = six.moves.urllib.parse.quote_plus(str(admin_id))
        path = '/admin/v1/admins/%s' % admin_id
        params = {}
        if name is not None:
            params['name'] = name
        if phone is not None:
            params['phone'] = phone
        if password is not None:
            params['password'] = password
        response = self.json_api_call('POST', path, params)
        return response


    def delete_admin(self, admin_id):
        """
        Deletes an administrator.

        admin_id - The id of the administrator.

        Raises RuntimeError on error.
        """
        admin_id = six.moves.urllib.parse.quote_plus(str(admin_id))
        path = '/admin/v1/admins/%s' % admin_id
        return self.json_api_call('DELETE', path, {})


    def reset_admin(self, admin_id):
        """
        Resets the admin lockout.

        admin_id - <int:admin id>

        Raises RuntimeError on error.
        """
        admin_id = six.moves.urllib.parse.quote_plus(str(admin_id))
        path = '/admin/v1/admins/%s/reset' % admin_id
        return self.json_api_call('POST', path, {})


    def activate_admin(self, email,
                       send_email=False,
                       valid_days=None):
        """
        Generates an activate code for an administrator and optionally
        emails the administrator.

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
        params = {}
        if email is not None:
            params['email'] = email
        if send_email is not None:
            params['send_email'] = '1' if send_email else '0'
        if valid_days is not None:
            params['valid_days'] = str(valid_days)
        response = self.json_api_call('POST',
                                      '/admin/v1/admins/activate',
                                      params)
        return response

    def get_logo(self):
        """
        Returns current logo's PNG data or raises an error if none is set.

        Raises RuntimeError on error.
        """
        response, data = self.api_call('GET',
                                       '/admin/v1/logo',
                                       params={})
        content_type = response.getheader('Content-Type')
        if content_type and content_type.startswith('image/'):
            return data
        else:
            return self.parse_json_response(response, data)

    def update_logo(self, logo):
        """
        Set a logo that will appear in future Duo Mobile activations.

        logo - <str:PNG byte sequence>

        Raises RuntimeError on error.
        """
        params = {
            'logo': logo.encode('base64'),
        }
        return self.json_api_call('POST', '/admin/v1/logo', params)

    def delete_logo(self):
        return self.json_api_call('DELETE', '/admin/v1/logo', params={})
