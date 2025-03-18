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


ENDPOINTS

Endpoint objects are returned in the following format:

    {"username": <str:username>,
     "email": <str:email>,
     "epkey": <str:epkey>,
     "os_family": <str:os family>,
     "os_version": <str:os version>,
     "model": <str:model>,
     "type": <str:type>,
     "browsers": [<browser object, ...]|None}


BROWSERS

Browser objects are returned in the following format:
    {"browser_family": <str:browser family>,
     "browser_version": <str:browser version>,
     "flash_version": <str: flash version>,
     "java_version": <str: java version>}


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
     'pending_deletion_days': <int:days a user will be in pending deletion status>,
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
     'security_checkup_enabled': <bool:is the security checkup feature enabled>,
     'user_managers_can_put_users_in_bypass': <bool:can user managers put users in bypass status>,
     'email_activity_notification_enabled': <bool:can users get activity notifications via email>,
     'push_activity_notification_enabled': <bool:can users get activity notifications via Duo Mobile>,
     'unenrolled_user_lockout_threshold': <int:days until a user will be locked out due to being unenrolled>,
     'enrollment_universal_prompt_enabled': <bool:will email enrollment use Universal Prompt experience>,
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
     'visual_style': Deprecated; ignored if specified.}

See the adminapi docs for possible values for enroll_policy, ip_whitelist, and type.


ADMINISTRATIVE UNITS

Administrative unit objects are returned in the following format:

    {'admin_unit_id': <str:administrative unit id>,
     'name': <str:administrative unit name>,
     'description': <str:administrative unit description>,
     'restrict_by_groups': <bool:group restriction (0|1)>,
     'restrict_by_integrations': <bool:integration restriction (0|1)>,
     'admins': [<str:admin key>, ...],
     'groups': [<str:group key>, ...],
     'integrations': [<str:integration key>, ...],
    }


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

import base64
import json
import time
import urllib.parse
import warnings
from typing import List, Optional
from datetime import datetime, timedelta, timezone

from . import Accounts, client
from .logs.telephony import Telephony

USER_STATUS_ACTIVE = "active"
USER_STATUS_BYPASS = "bypass"
USER_STATUS_DISABLED = "disabled"
USER_STATUS_LOCKED_OUT = "locked out"

TOKEN_HOTP_6 = "h6"
TOKEN_HOTP_8 = "h8"
TOKEN_YUBIKEY = "yk"

VALID_AUTHLOG_REQUEST_PARAMS = [
    "mintime",
    "maxtime",
    "limit",
    "sort",
    "next_offset",
    "event_types",
    "reasons",
    "results",
    "users",
    "applications",
    "groups",
    "factors",
    "api_version",
    "assessment",
    "detections",
]

VALID_ACTIVITY_REQUEST_PARAMS = ["mintime", "maxtime", "limit", "sort", "next_offset"]


class Admin(client.Client):
    account_id = None

    def api_call(self, method, path, params):
        if self.account_id is not None:
            params['account_id'] = self.account_id

        return super(Admin, self).api_call(
            method,
            path,
            params,
        )


    @classmethod
    def _canonicalize_ip_whitelist(klass, ip_whitelist):
        if isinstance(ip_whitelist, str):
            return ip_whitelist
        else:
            return ','.join(ip_whitelist)
        pass

    @staticmethod
    def _canonicalize_bypass_codes(codes):
        if isinstance(codes, str):
            return codes
        else:
            return ','.join([str(int(code)) for code in codes])

    def get_administrative_units(self, admin_id=None, group_id=None,
                                 integration_key=None, limit=None, offset=0):
        """
        Retrieves a list of administrative units optionally filtered by admin,
            group, or integration. At most one of admin_id, group_id, or
            integration_key should be passed.

        Args:
            admin_id(str): id of admin (optional)
            group_id(str): id of group (optional)
            integration_key(str): id of integration (optional)
            limit: The max number of administrative units to fetch at once.
                   Default None
            offset: If a limit is passed, the offset to start retrieval.
                    Default 0

        Returns: list of administrative units

        Raises RuntimeError on error.
        """
        (limit, offset) = self.normalize_paging_args(limit, offset)

        params = {}
        if admin_id is not None:
            params['admin_id'] = admin_id
        if group_id is not None:
            params['group_id'] = group_id
        if integration_key is not None:
            params['integration_key'] = integration_key

        if limit:
            params['limit'] = limit
            params['offset'] = offset

            return self.json_api_call('GET',
                                      '/admin/v1/administrative_units',
                                      params)

        iterator = self.get_administrative_units_iterator(
            admin_id, group_id, integration_key)

        return list(iterator)

    def get_administrative_units_iterator(self, admin_id=None, group_id=None,
                                          integration_key=None, ):
        """
        Provides a generator which produces administrative_units. Under the
        hood, this generator uses pagination, so it will only store one page of
        administrative_units at a time in memory.

        Returns: A generator which produces administrative_units.

        Raises RuntimeError on error.
        """
        params = {}
        if admin_id is not None:
            params['admin_id'] = admin_id
        if group_id is not None:
            params['group_id'] = group_id
        if integration_key is not None:
            params['integration_key'] = integration_key
        return self.json_paging_api_call('GET',
                                         '/admin/v1/administrative_units',
                                         params)

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

    def get_offline_log(self,
                        mintime=0):
        """
        Returns offline enrollment log events.

        mintime - Fetch events only >= mintime (to avoid duplicate
                  records that have already been fetched)

        Returns:
            [
                {'timestamp': <int:unix timestamp>,
                 'username': <str:username>,
                 'action': <str:action>,
                 'object': <str:object name>|None,
                 'description': <str:description>|None}, ...
            ]

        <action> is one of:
            'o2fa_user_provisioned',
            'o2fa_user_deprovisioned',
            'o2fa_user_reenrolled'

        Raises RuntimeError on error.
        """
        # Sanity check mintime as unix timestamp, then transform to string
        mintime = str(int(mintime))
        params = {
            'mintime': mintime,
        }
        response = self.json_api_call(
            'GET',
            '/admin/v1/logs/offline_enrollment',
            params,
        )
        return response

    def get_authentication_log(self, api_version=1, **kwargs):
        """
        Returns authentication log events.

        api_version - The api version of the handler to use. Currently, the
                      default api version is v1, but the v1 api will be
                      deprecated in a future version of the Duo Admin API.
                      Please migrate to the v2 api at your earliest convenience.
                      For details on the differences between v1 and v2,
                      please see Duo's Admin API documentation. (Optional)

        API Version v1:

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
                 'new_enrollment': <bool:if event corresponds to enrollment>,
                 'integration': <str:integration>,
                 'location': {
                     'state': '<str:state>',
                     'city': '<str:city>',
                     'country': '<str:country>'
                 }
             }]

        Raises RuntimeError on error.

        API Version v2:

        mintime (required) - Unix timestamp in ms; fetch records >= mintime
        maxtime (required) - Unix timestamp in ms; fetch records <= maxtime
        limit - Number of results to limit to
        next_offset - Used to grab the next set of results from a previous response
        sort - Sort order to be applied
        users - List of user ids to filter on
        groups - List of group ids to filter on
        applications - List of application ids to filter on
        results - List of results to filter to filter on
        reasons - List of reasons to filter to filter on
        factors - List of factors to filter on
        event_types - List of event_types to filter on

        Returns:
            {
                "authlogs": [
                {
                  "access_device": {
                    "ip": <str:ip address>,
                    "location": {
                      "city": <str:city>,
                      "state": <str:state>,
                      "country": <str:country
                    }
                  },
                  "application": {
                    "key": <str:application id>,
                    "name": <str:application name>
                  },
                  "auth_device": {
                    "ip": <str:ip address>,
                    "location": {
                      "city": <str:city>,
                      "state": <str:state>,
                      "country": <str:country
                    },
                    "name": <str:device name>
                  },
                  "event_type": <str:type>,
                  "factor": <str:factor,
                  "reason": <str:reason>,
                  "result": <str:result>,
                  "timestamp": <int:unix timestamp>,
                  "user": {
                    "key": <str:user id>,
                    "name": <str:user name>
                  }
                }
              ],
              "metadata": {
                "next_offset": [
                  <str>,
                  <str>
                ],
                "total_objects": <int>
              }
            }

        Raises RuntimeError on error.
        """

        if api_version not in [1,2]:
            raise ValueError("Invalid API Version")

        params = {}

        if api_version == 1: #v1
            params['mintime'] = kwargs['mintime'] if 'mintime' in kwargs else 0;
            # Sanity check mintime as unix timestamp, then transform to string
            params['mintime'] = '{:d}'.format(int(params['mintime']))
            warnings.warn(
                'The v1 Admin API for retrieving authentication log events '
                'will be deprecated in a future release of the Duo Admin API. '
                'Please migrate to the v2 API.',
            DeprecationWarning)
        else: #v2
            for k in kwargs:
                if kwargs[k] is not None and k in VALID_AUTHLOG_REQUEST_PARAMS:
                    params[k] = kwargs[k]

            if 'mintime' not in params:
                params['mintime'] = (int(time.time()) - 86400) * 1000
            # Sanity check mintime as unix timestamp, then transform to string
            params['mintime'] = '{:d}'.format(int(params['mintime']))


            if 'maxtime' not in params:
                params['maxtime'] = int(time.time()) * 1000
            # Sanity check maxtime as unix timestamp, then transform to string
            params['maxtime'] = '{:d}'.format(int(params['maxtime']))


        response = self.json_api_call(
            'GET',
            '/admin/v{}/logs/authentication'.format(api_version),
            params,
        )

        if api_version == 1:
            for row in response:
                row['eventtype'] = 'authentication'
                row['host'] = self.host
        else:
            for row in response['authlogs']:
                row['eventtype'] = 'authentication'
                row['host'] = self.host
        return response

    def get_activity_logs(self, **kwargs):
        """
        Returns activity log events.

        The activity endpoint is in public preview and subject to change.

        mintime - Unix timestamp in ms; fetch records >= mintime
        maxtime - Unix timestamp in ms; fetch records <= maxtime
        limit - Number of results to limit to
        next_offset - Used to grab the next set of results from a previous response
        sort - Sort order to be applied

        Returns:
            {
                "items": [
                    {
                        "access_device": {
                            "browser": <str:browser>,
                            "browser_version": <str:browser version>,
                            "ip": {
                                "address":  <str:ip address>
                            },
                            "location": {
                                "city":  <str:city>,
                                "country":  <str:country>,
                                "state": <str:state>
                            },
                            "os":  <str:os name>,
                            "os_version":  <str:os_version>
                        },
                        "action":  <str:action>,
                        "activity_id":  <str:activity id>,
                        "actor": {
                            "details": <str:json for actor details>
                            "key" :  <str:actor's key>,
                            "name":  <str:actor's name>,
                            "type":  <str:actor type>
                        },
                        "akey":  <str:akey>,
                        "application": {
                            "key":  <str:application's key>,
                            "name":  <str:application's name>,
                            "type":  <str:application's type>
                        },
                        "target": {
                            "details":  <str:target's details if available> ,
                            "key" :  <str:target's key>,
                            "name":  <str:target's name>,
                            "type":  <str:target's type>
                        },
                        "ts":  <str:timestamp captured for activity>
                    },
                ],
                "metadata": {
                    "next_offset": <str: comma seperated ts and offset value>
                    "total_objects": {
                        "relation" : <str: relational operator>
                        "value" : <int: total objects in the time range>
                    }
                }
            }

        Raises RuntimeError on error.
        """
        params = {}
        today = datetime.now(tz=timezone.utc)
        default_maxtime = int(today.timestamp() * 1000)
        default_mintime = int((today - timedelta(days=180)).timestamp() * 1000)

        for k in kwargs:
            if kwargs[k] is not None and k in VALID_ACTIVITY_REQUEST_PARAMS:
                params[k] = kwargs[k]

        if 'mintime' not in params:
            # If mintime is not provided, the script defaults it to 180 days in past
            params['mintime'] = default_mintime
        params['mintime'] = str(int(params['mintime']))
        if 'maxtime' not in params:
            #if maxtime is not provided, the script defaults it to now
            params['maxtime'] = default_maxtime
        params['maxtime'] = str(int(params['maxtime']))
        if 'limit' in params:
            params['limit'] = str(int(params['limit']))

        response = self.json_api_call(
            'GET',
            '/admin/v2/logs/activity',
            params,
        )
        for row in response['items']:
            row['eventtype'] = 'activity'
            row['host'] = self.host
        return response

    def get_telephony_log(self, mintime=0, api_version=1, **kwargs):
        """
        Returns telephony log events.

        mintime - Fetch events only >= mintime (to avoid duplicate
            records that have already been fetched)
        api_version - The API version of the handler to use.
            Currently, the default api version is v1, but the v1 API
            will be deprecated in a future version of the Duo Admin API.
            Please migrate to the v2 api at your earliest convenience.
            For details on the differences between v1 and v2,
            please see Duo's Admin API documentation. (Optional)

        v1 Returns:
            [
                {
                    'timestamp': <int:unix timestamp>,
                    'eventtype': "telephony",
                    'host': <str:host>,
                    'context': <str:context>,
                    'type': <str:type>,
                    'phone': <str:phone number>,
                    'credits': <str:credits>}
            ]

        v2 Returns:
            {
                "items": [
                    {
                        'context': <str>,
                        'credits': <int: credits used>,
                        'phone': <str:phone number>,
                        'telephony_id': <str:UUID>,
                        'ts': <str:ISO timestamp>,
                        'txid': <str:UUID>,
                        'type': <str:"sms" or "phone">,
                        'eventtype': <str:"telephony">,
                        'host': <str:application hostname>
                    }
                ],
                "metadata": {
                    "next_offset": <str: comma seperated ts and offset value>
                    "total_objects": {
                        "relation" : <str: relational operator>
                        "value" : <int: total objects in the time range>
                    }
                }
            }

        Raises RuntimeError on error.
        """

        if api_version not in [1,2]:
            raise ValueError("Invalid API Version")

        if api_version == 2:
            return Telephony.get_telephony_logs_v2(self.json_api_call, self.host, **kwargs)
        return Telephony.get_telephony_logs_v1(self.json_api_call, self.host, mintime=mintime)

    def get_users_iterator(self):
        """
        Returns iterator of user objects.

        Raises RuntimeError on error.
        """
        return self.json_paging_api_call('GET', '/admin/v1/users', {})

    def get_users(self, limit=None, offset=0):
        """
        Returns a list of user objects.

        Params:
            limit - The maximum number of records to return. (Optional)
            offset - The offset of the first record to return. (Optional)

        Raises RuntimeError on error.
        """
        (limit, offset) = self.normalize_paging_args(limit, offset)
        if limit:
            return self.json_api_call(
                'GET', '/admin/v1/users', {'limit': limit, 'offset': offset})

        return list(self.get_users_iterator())

    def get_user_by_id(self, user_id):
        """
        Returns user specified by user_id.

        user_id - User to fetch

        Returns user object.

        Raises RuntimeError on error.
        """
        user_id = urllib.parse.quote_plus(str(user_id))
        path = '/admin/v1/users/' + user_id
        response = self.json_api_call('GET', path, {})
        return response

    def get_user_by_email(self, email):
        """
        Returns user specified by email.

        email - User to fetch

        Returns user object.

        Raises RuntimeError on error.
        """
        params = {
            'email': email,
        }
        response = self.json_api_call('GET',
                                      '/admin/v1/users',
                                      params)
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

    def get_users_by_names(self, usernames):
        """
        Returns users specified by usernames.

        usernames - Users to fetch

        Returns a list user objects matching usernames (or aliases).

        Raises RuntimeError on error.
        """
        username_list = json.dumps(usernames)
        params = {
            'username_list': username_list,
        }
        response = self.json_paging_api_call('GET',
                                             '/admin/v1/users',
                                             params)
        return response

    def get_users_by_ids(self, user_ids):
        """
        Returns users specified by user ids.

        user_ids - Users to fetch

        Returns a list user objects matching user ids.

        Raises RuntimeError on error.
        """
        user_id_list = json.dumps(user_ids)
        params = {
            'user_id_list': user_id_list,
        }
        response = self.json_paging_api_call('GET',
                                             '/admin/v1/users',
                                             params)
        return response

    def add_user(self, username, realname=None, status=None,
                 notes=None, email=None, firstname=None, lastname=None,
                 alias1=None, alias2=None, alias3=None, alias4=None,
                 aliases=None):
        """
        Adds a user.

        username - Username
        realname - User's real name (optional)
        status - User's status, defaults to USER_STATUS_ACTIVE
        notes - Comment field (optional)
        email - Email address (optional)
        firstname - User's given name for ID Proofing (optional)
        lastname - User's surname for ID Proofing (optional)
        alias1..alias4 - Aliases for the user's primary username (optional)
        aliases - Aliases for the user's primary username (optional)

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
        if firstname is not None:
            params['firstname'] = firstname
        if lastname is not None:
            params['lastname'] = lastname
        if alias1 is not None:
            params['alias1'] = alias1
        if alias2 is not None:
            params['alias2'] = alias2
        if alias3 is not None:
            params['alias3'] = alias3
        if alias4 is not None:
            params['alias4'] = alias4
        if aliases is not None:
            params['aliases'] = aliases
        response = self.json_api_call('POST',
                                      '/admin/v1/users',
                                      params)
        return response

    def update_user(self, user_id, username=None, realname=None, status=None,
                    notes=None, email=None, firstname=None, lastname=None,
                    alias1=None, alias2=None, alias3=None, alias4=None,
                    aliases=None):
        """
        Update username, realname, status, or notes for a user.

        user_id - User ID
        username - Username (optional)
        realname - User's real name (optional)
        status - User's status, defaults to USER_STATUS_ACTIVE
        notes - Comment field (optional)
        email - Email address (optional)
        firstname - User's given name for ID Proofing (optional)
        lastname - User's surname for ID Proofing (optional)
        alias1..alias4 - Aliases for the user's primary username (optional)
        aliases - Aliases for the user's primary username. (optional)

        Returns updated user object.

        Raises RuntimeError on error.
        """
        user_id = urllib.parse.quote_plus(str(user_id))
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
        if firstname is not None:
            params['firstname'] = firstname
        if lastname is not None:
            params['lastname'] = lastname
        if alias1 is not None:
            params['alias1'] = alias1
        if alias2 is not None:
            params['alias2'] = alias2
        if alias3 is not None:
            params['alias3'] = alias3
        if alias4 is not None:
            params['alias4'] = alias4
        if aliases is not None:
            params['aliases'] = aliases
        response = self.json_api_call('POST', path, params)
        return response

    def delete_user(self, user_id):
        """
        Deletes a user. If the user is already deleted, does nothing.

        user_id - User ID

        Raises RuntimeError on error.
        """
        user_id = urllib.parse.quote_plus(str(user_id))
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

    def add_user_bypass_codes(
        self, 
        user_id, 
        count=None, 
        valid_secs=None, 
        remaining_uses=None, 
        codes=None, 
        preserve_existing=None,
        endpoint_verification=None,
    ):
        """
        Generate bypass codes for user.
        Replaces a user's bypass codes with new codes unless
        `preserve_existing=True` is passed.

        user_id                 User ID
        count                   Number of new codes to randomly generate
        valid_secs              Seconds before codes expire (if 0 they will never expire)
        remaining_uses          The number of times this code can be used (0 is unlimited)
        codes                   Optionally provide custom codes, otherwise will be random
                                count and codes are mutually exclusive
        preserve_existing       whether to preserve existing codes when creating new ones,
                                default is to remove existing bypass codes
        endpoint_verification   New argument for unreleased feature. Will be ignored if used.
                                Client will be updated again in the future when feature is released.

        Returns a list of newly created codes.

        Raises RuntimeError on error.
        """
        user_id = urllib.parse.quote_plus(str(user_id))
        path = '/admin/v1/users/' + user_id + '/bypass_codes'
        params = {}

        if count is not None:
            params['count'] = str(int(count))

        if valid_secs is not None:
            params['valid_secs'] = str(int(valid_secs))

        if endpoint_verification is not None:
            params["endpoint_verification"] = str(endpoint_verification).lower()

        if remaining_uses is not None:
            params['reuse_count'] = str(int(remaining_uses))

        if codes is not None:
            params['codes'] = self._canonicalize_bypass_codes(codes)

        if preserve_existing is not None:
            params['preserve_existing'] = preserve_existing

        return self.json_api_call('POST', path, params)

    def get_user_bypass_codes_iterator(self, user_id):
        """ Returns an iterator of bypass codes associated with a user.

            Params:
                user_id (str) - The user id.

            Returns:
                A iterator yielding bypass code dicts.

            Notes:
                Raises RuntimeError on error.
        """
        user_id = urllib.parse.quote_plus(str(user_id))
        path = '/admin/v1/users/' + user_id + '/bypass_codes'
        return self.json_paging_api_call('GET', path, {})


    def get_user_bypass_codes(self, user_id, limit=None, offset=0):
        """ Returns a list of bypass codes associated with a user.

            Params:
                user_id (str) - The user id.
                limit - The maximum number of records to return. (Optional)
                offset - The offset of the first record to return. (Optional)

            Returns:
                An array of bypass code dicts.

            Notes:
                Raises RuntimeError on error.
        """
        (limit, offset) = self.normalize_paging_args(limit, offset)
        if limit:
            user_id = urllib.parse.quote_plus(str(user_id))
            path = '/admin/v1/users/' + user_id + '/bypass_codes'
            return self.json_api_call(
                'GET', path, {'limit': limit, 'offset': offset})

        return list(self.get_user_bypass_codes_iterator(user_id))

    def get_user_phones_iterator(self, user_id):
        """
        Returns an iterator of phones associated with the user.

        user_id - User ID

        Returns an iterator of phone objects.

        Raises RuntimeError on error.
        """
        user_id = urllib.parse.quote_plus(str(user_id))
        path = '/admin/v1/users/' + user_id + '/phones'
        return self.json_paging_api_call('GET', path, {})

    def get_user_phones(self, user_id, limit=None, offset=0):
        """
        Returns an array of phones associated with the user.

        user_id - User ID
        limit - The maximum number of records to return. (Optional)
        offset - The offset of the first record to return. (Optional)

        Returns list of phone objects.

        Raises RuntimeError on error.
        """
        (limit, offset) = self.normalize_paging_args(limit, offset)
        if limit:
            user_id = urllib.parse.quote_plus(str(user_id))
            path = '/admin/v1/users/' + user_id + '/phones'
            return self.json_api_call(
                'GET', path, {'limit': limit, 'offset': offset})

        return list(self.get_user_phones_iterator(user_id))

    def add_user_phone(self, user_id, phone_id):
        """
        Associates a phone with a user.

        user_id - User ID
        phone_id - Phone ID

        Returns nothing.

        Raises RuntimeError on error.
        """
        user_id = urllib.parse.quote_plus(str(user_id))
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
        user_id = urllib.parse.quote_plus(str(user_id))
        path = '/admin/v1/users/' + user_id + '/phones/' + phone_id
        params = {}
        return self.json_api_call('DELETE', path,
                                    params)

    def get_user_tokens_iterator(self, user_id):
        """
        Returns an iterator of hardware tokens associated with the user.

        user_id - User ID

        Returns iterator of hardware token objects.

        Raises RuntimeError on error.
        """
        user_id = urllib.parse.quote_plus(str(user_id))
        path = '/admin/v1/users/' + user_id + '/tokens'
        return self.json_paging_api_call('GET', path, {})

    def get_user_tokens(self, user_id, limit=None, offset=0):
        """
        Returns an array of hardware tokens associated with the user.

        user_id - User ID
        limit - The maximum number of records to return. (Optional)
        offset - The offset of the first record to return. (Optional)

        Returns list of hardware token objects.

        Raises RuntimeError on error.
        """
        (limit, offset) = self.normalize_paging_args(limit, offset)
        if limit:
            user_id = urllib.parse.quote_plus(str(user_id))
            path = '/admin/v1/users/' + user_id + '/tokens'
            return self.json_api_call(
                'GET', path, {'limit': limit, 'offset': offset})

        return list(self.get_user_tokens_iterator(user_id))

    def add_user_token(self, user_id, token_id):
        """
        Associates a hardware token with a user.

        user_id - User ID
        token_id - Token ID

        Returns nothing.

        Raises RuntimeError on error.
        """
        user_id = urllib.parse.quote_plus(str(user_id))
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
        user_id = urllib.parse.quote_plus(str(user_id))
        token_id = urllib.parse.quote_plus(str(token_id))
        path = '/admin/v1/users/' + user_id + '/tokens/' + token_id
        return self.json_api_call('DELETE', path, {})

    def get_user_u2ftokens_iterator(self, user_id):
        """ Returns an iterator of u2ftokens associated with a user.

            Params:
                user_id (str) - The user id.

            Returns:
                A generator yielding u2ftoken dicts.

            Notes:
                Raises RuntimeError on error.
        """
        user_id = urllib.parse.quote_plus(str(user_id))
        path = '/admin/v1/users/' + user_id + '/u2ftokens'
        return self.json_paging_api_call('GET', path, {})

    def get_user_u2ftokens(self, user_id, limit=None, offset=0):
        """ Returns an array of u2ftokens associated with a user.

            Params:
                user_id (str) - The user id.
                limit - The maximum number of records to return. (Optional)
                offset - The offset of the first record to return. (Optional)

            Returns:
                An array of u2ftoken dicts.

            Notes:
                Raises RuntimeError on error.
        """
        (limit, offset) = self.normalize_paging_args(limit, offset)
        if limit:
            user_id = urllib.parse.quote_plus(str(user_id))
            path = '/admin/v1/users/' + user_id + '/u2ftokens'
            return self.json_api_call(
                'GET', path, {'limit': limit, 'offset': offset})

        return list(self.get_user_u2ftokens_iterator(user_id))

    def get_user_webauthncredentials_iterator(self, user_id):
        """ Returns an iterator of webauthncredentials associated with a user.

            Params:
                user_id (str) - The user id.

            Returns:
                A generator yielding webauthncredentials dicts.

            Notes:
                Raises RuntimeError on error.
        """
        user_id = urllib.parse.quote_plus(str(user_id))
        path = '/admin/v1/users/' + user_id + '/webauthncredentials'
        return self.json_paging_api_call('GET', path, {})

    def get_user_webauthncredentials(self, user_id, limit=None, offset=0):
        """ Returns an array of webauthncredentials associated
            with a user.

            Params:
                user_id (str) - The user id.
                limit - The maximum number of records to return. (Optional)
                offset - The offset of the first record to return. (Optional)

            Returns:
                An array of webauthncredentials dicts.

            Notes:
                Raises RuntimeError on error.
        """
        (limit, offset) = self.normalize_paging_args(limit, offset)
        if limit:
            user_id = urllib.parse.quote_plus(str(user_id))
            path = '/admin/v1/users/' + user_id + '/webauthncredentials'
            return self.json_api_call(
                'GET', path, {'limit': limit, 'offset': offset})

        return list(self.get_user_webauthncredentials_iterator(user_id))

    def get_user_groups_iterator(self, user_id):
        """
        Returns an iterator of groups associated with the user.

        user_id - User ID

        Returns iterator of groups objects.

        Raises RuntimeError on error.
        """
        user_id = urllib.parse.quote_plus(str(user_id))
        path = '/admin/v1/users/' + user_id + '/groups'
        return self.json_paging_api_call('GET', path, {})

    def get_user_groups(self, user_id, limit=None, offset=0):
        """
        Returns an array of groups associated with the user.

        user_id - User ID
        limit - The maximum number of records to return. (Optional)
        offset - The offset of the first record to return. (Optional)

        Returns list of groups objects.

        Raises RuntimeError on error.
        """
        (limit, offset) = self.normalize_paging_args(limit, offset)
        if limit:
            user_id = urllib.parse.quote_plus(str(user_id))
            path = '/admin/v1/users/' + user_id + '/groups'
            return self.json_api_call(
                'GET', path, {'limit': limit, 'offset': offset})

        return list(self.get_user_groups_iterator(user_id))

    def add_user_group(self, user_id, group_id):
        """
        Associates a group with a user.

        user_id - User ID
        group_id - Group ID

        Returns nothing.

        Raises RuntimeError on error.
        """
        user_id = urllib.parse.quote_plus(str(user_id))
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
        user_id = urllib.parse.quote_plus(str(user_id))
        path = '/admin/v1/users/' + user_id + '/groups/' + group_id
        params = {}
        return self.json_api_call('DELETE', path, params)

    def get_endpoint(self, epkey):
        """
        Get a single endpoint from the AdminAPI by a supplied epkey.

        Params:
            epkey (str) - The supplied endpoint key to fetch.

        Returns: The endpoint object represented as a dict.
        Raises:
            RuntimeError: if the request returns a non-200 status response.
        """
        escaped_epkey = urllib.parse.quote_plus(str(epkey))
        path = '/admin/v1/endpoints/' + escaped_epkey
        return self.json_api_call('GET', path, {})

    def get_endpoints_iterator(self):
        """
        Returns iterator of endpoints objects.

        Raises RuntimeError on error.
        """
        return self.json_paging_api_call('GET', '/admin/v1/endpoints', {})

    def get_endpoints(self, limit=None, offset=0):
        """
        Returns a list of endpoints.

        Params:
            limit - The maximum number of records to return. (Optional)
            offset - The offset of the first record to return. (Optional)

        Raises RuntimeError on error.
        """
        (limit, offset) = self.normalize_paging_args(limit, offset)
        if limit:
            return self.json_api_call('GET', '/admin/v1/endpoints',
                                      {'limit': limit, 'offset': offset})

        return list(self.get_endpoints_iterator())

    def get_phones_generator(self):
        """
        Returns a generator yielding phones.
        """
        return self.json_paging_api_call(
            'GET',
            '/admin/v1/phones',
            {}
        )

    def get_phones(self, limit=None, offset=0):
        """
        Retrieves a list of phones.
        Args:
            limit: The max number of admins to fetch at once. Default None
            offset: If a limit is passed, the offset to start retrieval.
                    Default 0

        Returns: list of phones

        Raises RuntimeError on error.
        """
        (limit, offset) = self.normalize_paging_args(limit, offset)
        if limit:
            return self.json_api_call(
                'GET',
                '/admin/v1/phones',
                {'limit': limit, 'offset': offset}
            )

        return list(self.get_phones_generator())

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
        phone_id = urllib.parse.quote_plus(str(phone_id))
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

    def get_desktoptokens_generator(self):
        """
        Returns a generator yielding desktoptokens.
        """
        return self.json_paging_api_call(
            'GET',
            '/admin/v1/desktoptokens',
            {}
        )

    def get_desktoptokens(self, limit=None, offset=0):
        """
        Retrieves a list of desktoptokens.
        Args:
            limit: The max number of admins to fetch at once. Default None
            offset: If a limit is passed, the offset to start retrieval.
                    Default 0

        Returns: list of desktoptokens

        Raises RuntimeError on error.

        """
        (limit, offset) = self.normalize_paging_args(limit, offset)
        if limit:
            return self.json_api_call(
                'GET',
                '/admin/v1/desktoptokens',
                {'limit': limit, 'offset': offset}
            )

        return list(self.get_desktoptokens_generator())

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
        path = '/admin/v1/desktoptokens/' + urllib.parse.quote_plus(desktoptoken_id)
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
        desktoptoken_id = urllib.parse.quote_plus(str(desktoptoken_id))
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
        quoted_id = urllib.parse.quote_plus(desktoptoken_id)
        response = self.json_api_call('POST',
            '/admin/v1/desktoptokens/%s/activate' % quoted_id,
            params)
        return response

    def get_tokens_generator(self):
        """
        Returns a generator yielding tokens.
        """
        return self.json_paging_api_call(
            'GET',
            '/admin/v1/tokens',
            {}
        )

    def get_tokens(self, limit=None, offset=0):
        """
        Retrieves a list of tokens.
        Args:
            limit: The max number of admins to fetch at once. Default None
            offset: If a limit is passed, the offset to start retrieval.
                    Default 0

        Returns: list of tokens

        Raises RuntimeError on error.
        """
        (limit, offset) = self.normalize_paging_args(limit, offset)
        if limit:
            return self.json_api_call(
                'GET',
                '/admin/v1/tokens',
                {'limit': limit, 'offset': offset}
            )

        return list(self.get_tokens_generator())

    def get_token_by_id(self, token_id):
        """
        Returns a token.

        token_id - Token ID

        Returns a token object.
        """
        token_id = urllib.parse.quote_plus(str(token_id))
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
        token_id = urllib.parse.quote_plus(str(token_id))
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
        token_id = urllib.parse.quote_plus(str(token_id))
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
        token_id = urllib.parse.quote_plus(str(token_id))
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
                        pending_deletion_days=None,
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
                        password_requires_special=None,
                        helpdesk_bypass=None,
                        helpdesk_bypass_expiration=None,
                        helpdesk_message=None,
                        helpdesk_can_send_enroll_email=None,
                        reactivation_url=None,
                        reactivation_integration_key=None,
                        security_checkup_enabled=None,
                        user_managers_can_put_users_in_bypass=None,
                        email_activity_notification_enabled=None,
                        push_activity_notification_enabled=None,
                        unenrolled_user_lockout_threshold=None,
                        enrollment_universal_prompt_enabled=None,
                        ):
        """
        Update settings.

        lockout_threshold - <int:number of attempts>|None
        lockout_expire_duration - <int:minutes>|0|None
        inactive_user_expiration - <int:number of days>|None
        pending_deletion_days - <int:number of days>|None
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
        push_enabled - Deprecated; ignored if specified.
        sms_enabled - Deprecated; ignored if specified.
        voice_enabled - Deprecated; ignored if specified.
        mobile_otp_enabled - Deprecated; ignored if specified.
        u2f_enabled - Deprecated; ignored if specified.
        user_telephony_cost_max - <int:positive number of credits>
        minimum_password_length - <int:length>|None
        password_requires_upper_alpha - True|False|None
        password_requires_lower_alpha - True|False|None
        password_requires_numeric - True|False|None
        password_requires_special - True|False|None
        helpdesk_bypass - "allow"|"limit"|"deny"|None
        helpdesk_bypass_expiration - <int:minutes>|0
        helpdesk_message - <str:message|None>
        helpdesk_can_send_enroll_email - True|False|None
        reactivation_url - <str:url>|None
        reactivation_integration_key - <str:url>|None
        security_checkup_enabled - True|False|None
        user_managers_can_put_users_in_bypass - True|False|None
        email_activity_notification_enabled = True|False|None
        push_activity_notification_enabled = True|False|None
        unenrolled_user_lockout_threshold = <int:number of days>|0|None
        enrollment_universal_prompt_enabled = True|False|None

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
        if pending_deletion_days is not None:
            params['pending_deletion_days'] = str(pending_deletion_days)
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
            params['fraud_email_enabled'] = ('1' if
                fraud_email_enabled else '0')
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
        if helpdesk_bypass is not None:
            params['helpdesk_bypass'] = str(helpdesk_bypass)
        if helpdesk_bypass_expiration is not None:
            params['helpdesk_bypass_expiration'] = str(helpdesk_bypass_expiration)
        if helpdesk_message is not None:
            params['helpdesk_message'] = str(helpdesk_message)
        if helpdesk_can_send_enroll_email is not None:
            params['helpdesk_can_send_enroll_email'] = ('1' if
              helpdesk_can_send_enroll_email else '0')
        if reactivation_url is not None:
            params['reactivation_url'] = reactivation_url
        if reactivation_integration_key is not None:
            params['reactivation_integration_key'] = reactivation_integration_key
        if security_checkup_enabled is not None:
            params['security_checkup_enabled'] = ('1' if
                security_checkup_enabled else '0')
        if user_managers_can_put_users_in_bypass is not None:
            params['user_managers_can_put_users_in_bypass'] = ('1' if
                user_managers_can_put_users_in_bypass else '0')
        if email_activity_notification_enabled is not None:
            params['email_activity_notification_enabled'] = (
                '1' if email_activity_notification_enabled else '0'
            )
        if push_activity_notification_enabled is not None:
            params['push_activity_notification_enabled'] = (
                '1' if push_activity_notification_enabled else '0'
            )
        if unenrolled_user_lockout_threshold is not None:
            params['unenrolled_user_lockout_threshold'] = str(
                unenrolled_user_lockout_threshold
            )
        if enrollment_universal_prompt_enabled is not None:
            params['enrollment_universal_prompt_enabled'] = (
                '1' if enrollment_universal_prompt_enabled else '0'
            )

        if not params:
            raise TypeError("No settings were provided")

        response = self.json_api_call('POST',
                                      '/admin/v1/settings',
                                      params)
        return response

    def set_allowed_admin_auth_methods(self,
                                        push_enabled=None,
                                        sms_enabled=None,
                                        voice_enabled=None,
                                        mobile_otp_enabled=None,
                                        yubikey_enabled=None,
                                        hardware_token_enabled=None,
                                        verified_push_enabled=None,
                                        verified_push_length=None
                                        ):
        params = {}
        if push_enabled is not None:
            params['push_enabled'] = (
                '1' if push_enabled else '0')
        if sms_enabled is not None:
            params['sms_enabled'] = (
                '1' if sms_enabled else '0')
        if mobile_otp_enabled is not None:
            params['mobile_otp_enabled'] = (
                '1' if mobile_otp_enabled else '0')
        if hardware_token_enabled is not None:
            params['hardware_token_enabled'] = (
                '1' if hardware_token_enabled else '0')
        if yubikey_enabled is not None:
            params['yubikey_enabled'] = (
                '1' if yubikey_enabled else '0')
        if voice_enabled is not None:
            params['voice_enabled'] = (
                '1' if voice_enabled else '0')
        if verified_push_enabled is not None:
            params['verified_push_enabled'] = (
                '1' if verified_push_enabled else '0')
            if params['verified_push_enabled'] == '1':
                params['verified_push_length'] = (
                    verified_push_length if verified_push_length is not None else 3)
        response = self.json_api_call(
            'POST',
            '/admin/v1/admins/allowed_auth_methods',
            params
        )
        return response

    def get_allowed_admin_auth_methods(self):
        params={}
        response = self.json_api_call(
            'GET',
            '/admin/v1/admins/allowed_auth_methods',
            params
        )
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

    def get_groups_generator(self):
        """
        Returns a generator yielding groups.
        """
        return self.json_paging_api_call(
            'GET',
            '/admin/v1/groups',
            {}
        )

    def get_groups_by_group_ids(self, group_ids):
        """
        Get a list of groups by their group ids

        Args:
            group_ids: list of group ids to fetch

        Returns:
            list of groups
        """
        group_id_list = json.dumps(group_ids)
        return self.json_api_call(
            'GET',
            '/admin/v1/groups',
            {'group_id_list': group_id_list}
        )

    def get_groups(self, limit=None, offset=0):
        """
        Retrieves a list of groups.
        Args:
            limit: The max number of groups to fetch at once. Default None
            offset: If a limit is passed, the offset to start retrieval.
                    Default 0

        Returns: list of groups

        Raises RuntimeError on error.

        """
        (limit, offset) = self.normalize_paging_args(limit, offset)
        if limit:
            return self.json_api_call(
                'GET',
                '/admin/v1/groups',
                {'limit': limit, 'offset': offset}
            )

        return list(self.get_groups_generator())

    def get_group(self, group_id, api_version=1):
        """
        Returns a group by the group id.

        group_id - The id of group (Required)
        api_version - The api version of the handler to use. Currently, the
                      default api version is v1, but the v1 api will be
                      deprecated in a future version of the Duo Admin API.
                      Please migrate to the v2 api at your earliest convenience.
                      For details on the differences between v1 and v2,
                      please see Duo's Admin API documentation. (Optional)
        """
        if api_version == 1:
            url = '/admin/v1/groups/'
            warnings.warn(
                'The v1 Admin API for group details will be deprecated '
                'in a future release of the Duo Admin API. Please migrate to '
                'the v2 API.',
                DeprecationWarning)
        elif api_version == 2:
            url = '/admin/v2/groups/'
        else:
            raise ValueError('Invalid API Version')

        return self.json_api_call('GET', url + group_id, {})

    def get_group_users(self, group_id, limit=None, offset=0):
        """
        Get a paginated list of users associated with the specified
        group.

        group_id - The id of the group (Required)
        limit - The maximum number of records to return. Maximum is 500. (Optional)
        offset - The offset of the first record to return. (Optional)
        """
        (limit, offset) = self.normalize_paging_args(limit, offset)
        if limit:
            return self.json_api_call(
                'GET',
                '/admin/v2/groups/' + group_id + '/users',
                {
                    'limit': limit,
                    'offset': offset,
                })
        return list(self.get_group_users_iterator(group_id))

    def get_group_users_iterator(self, group_id):
        """
        Returns an iterator of users associated with the specified group.

        group_id - The id of the group (Required)
        """
        return self.json_paging_api_call(
            'GET',
            '/admin/v2/groups/' + group_id + '/users',
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

    def delete_group(self, group_id):
        """
        Delete a group by group_id

        group_id - The id of the group (Required)
        """
        return self.json_api_call(
            'DELETE',
            '/admin/v1/groups/' + group_id,
            {}
        )

    def modify_group(self,
                     group_id,
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

        group_id - The id of the group to modify (Required)
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
            '/admin/v1/groups/' + group_id,
            params
        )
        return response

    def get_integrations_generator(self):
        """
        Returns a generator yielding integrations.
        """
        return self.json_paging_api_call(
            'GET',
            '/admin/v3/integrations',
            {},
        )

    def get_integrations(self, limit=None, offset=0):
        """
        Retrieves a list of integrations.
        Args:
            limit: The max number of admins to fetch at once. Default None
            offset: If a limit is passed, the offset to start retrieval.
                    Default 0

        Returns: list of integrations

        Raises RuntimeError on error.
        """
        (limit, offset) = self.normalize_paging_args(limit, offset)
        if limit:
            return self.json_api_call(
                'GET',
                '/admin/v3/integrations',
                {'limit': limit, 'offset': offset},
            )

        return list(self.get_integrations_generator())

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
            '/admin/v3/integrations/' + integration_key,
            params,
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
                           self_service_allowed=None,
                           sso=None,
                           user_access=None):
        """Creates a new integration.

        name - The name of the integration (required)
        integration_type - <str: integration type constant> (required)
                           See adminapi docs for possible values.
        visual_style - Deprecated; ignored if specified.
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
        sso - <dict: parameters for generic single sign-on> (optional)
                New argument for unreleased feature. Will return an error if used.
                Client will be updated again in the future when feature is released.

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
        if sso is not None:
            params['sso'] = sso
        if user_access is not None:
            params['user_access'] = user_access

        response = self.json_api_call('POST',
                                      '/admin/v3/integrations',
                                      params,
        )
        return response

    def get_registered_devices_generator(self):
        """
        Returns a generator yielding Duo Desktop registered devices.
        """
        return self.json_paging_api_call('GET', '/admin/v1/registered_devices', {})

    def get_registered_devices(self, limit=None, offset=0):
        """
        Retrieves a list of Duo Desktop registered devices.

        Args:
            limit: The max number of registered devices to fetch at once. [Default: None]
            offset: If a 'limit' is passed, the offset to start retrieval.
                    [Default: 0]

        Returns:
            list of registered devices

        Raises:
            RuntimeError on error.

        """
        (limit, offset) = self.normalize_paging_args(limit, offset)
        if limit:
            return self.json_api_call('GET', '/admin/v1/registered_devices', {'limit': limit, 'offset': offset})

        return list(self.get_registered_devices_generator())

    def get_registered_device_by_id(self, registered_device_id):
        """
        Returns a Duo Desktop registered device specified by registered_device_id (compkey).

        Args:
            registered_device_id - Duo Desktop registered device compkey

        Returns:
            registered device object.

        Raises:
             RuntimeError on error.
        """
        path = '/admin/v1/registered_devices/' + registered_device_id
        response = self.json_api_call('GET', path, {})
        return response

    def delete_registered_device(self, registered_device_id):
        """
        Deletes a Duo Desktop registered device. If the registered device has already been deleted,
        does nothing.

        Args:
            registered_device_id - Duo Desktop registered device ID (compkey).

        Returns:
             None

        Raises:
             RuntimeError on error.
        """
        path = '/admin/v1/registered_devices/' + urllib.parse.quote_plus(registered_device_id)
        params = {}
        return self.json_api_call('DELETE', path, params)

    def get_secret_key(self, integration_key):
        """Returns the secret key of the specified integration.

        integration_key - The ikey of the secret key to get.

        Returns the skey
        
        Raises RuntimeError on error.
        """
        params = {}
        response = self.json_api_call(
            'GET',
            '/admin/v1/integrations/' + integration_key + '/skey',
            params,
        )
        return response

    def delete_integration(self, integration_key):
        """Deletes an integration.

        integration_key - The integration key of the integration to delete.

        Raises RuntimeError on error.

        """
        integration_key = urllib.parse.quote_plus(str(integration_key))
        path = '/admin/v3/integrations/%s' % integration_key
        return self.json_api_call(
            'DELETE',
            path,
            {},
        )

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
                           self_service_allowed=None,
                           sso=None,
                           user_access=None
                           ):
        """Updates an integration.

        integration_key - The key of the integration to update. (required)
        name - The name of the integration (optional)
        visual_style - Deprecated; ignored if specified.
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
        sso - <dict: parameters for generic single sign-on> (optional)
                New argument for unreleased feature. Will return an error if used.
                Client will be updated again in the future when feature is released.

        If any value other than None is provided for 'reset_secret_key'
        (for example, 1), then a new secret key will be generated for the
        integration.

        Returns the created integration.

        Raises RuntimeError on error.

        """
        integration_key = urllib.parse.quote_plus(str(integration_key))
        path = '/admin/v3/integrations/%s' % integration_key
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
        if sso is not None:
            params['sso'] = sso
        if user_access is not None:
            params['user_access'] = user_access

        if not params:
            raise TypeError("No new values were provided")

        response = self.json_api_call(
            'POST',
            path,
            params,
        )
        return response

    def get_admins(self, limit=None, offset=0):
        """
        Retrieves a list of administrators.
        Args:
            limit: The max number of admins to fetch at once. Default None
            offset: If a limit is passed, the offset to start retrieval.
                    Default 0

        Returns: list of administrators. See the adminapi docs.

        Raises RuntimeError on error.

        """

        (limit, offset) = self.normalize_paging_args(limit, offset)
        if limit:
            return self.json_api_call(
                'GET',
                '/admin/v1/admins',
                {'limit': limit, 'offset': offset}
            )

        iterator = self.get_admins_iterator()

        return list(iterator)

    def get_admins_iterator(self):
        """
        Provides a generator which produces admins. Under the hood, this
        generator uses pagination, so it will only store one page of admins at a
        time in memory.

        Returns: A generator which produces admins.

        Raises RuntimeError on error.
        """
        return self.json_paging_api_call('GET', '/admin/v1/admins', {})

    def get_admin(self, admin_id):
        """
        Returns an administrator.

        admin_id - The id of the administrator.

        Returns an administrator.  See the adminapi docs.

        Raises RuntimeError on error.
        """
        admin_id = urllib.parse.quote_plus(str(admin_id))
        path = '/admin/v1/admins/%s' % admin_id
        response = self.json_api_call('GET', path, {})
        return response

    def add_admin(self, name, email, phone, password, role=None, subaccount_role=None):
        """
        Create an administrator and adds it to a customer.

        name - <str:the name of the administrator>
        email - <str:email address>
        phone - <str:phone number>
        password - Deprecated; ignored if specified.
        role - <str|None:role>
        subaccount_role - <str|None:role>

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
        if role is not None:
            params['role'] = role
        if subaccount_role is not None:
            params['subaccount_role'] = subaccount_role
        response = self.json_api_call('POST', '/admin/v1/admins', params)
        return response

    def update_admin(self, admin_id,
                     name=None,
                     phone=None,
                     password=None,
                     password_change_required=None,
                     status=None,
                     role=None,
                     subaccount_role=None
                     ):
        """
        Update one or more attributes of an administrator.

        admin_id - The id of the administrator.
        name - <str:the name of the administrator> (optional)
        phone - <str:phone number> (optional)
        password - Deprecated; ignored if specified.
        password_change_required - <bool|None:Whether admin is required to change their password at next login> (optional)
        status - the status of the administrator (optional) - NOTE: Valid values are "Active" and "Disabled" - "Disabled" NOT valid for administrators with role - Owner
        role - <str|None:role> (optional)
        subaccount_role - <str|None:role> (optional)

        Returns the updated administrator.  See the adminapi docs.

        Raises RuntimeError on error.
        """
        admin_id = urllib.parse.quote_plus(str(admin_id))
        path = '/admin/v1/admins/%s' % admin_id
        params = {}
        if name is not None:
            params['name'] = name
        if phone is not None:
            params['phone'] = phone
        if password_change_required is not None:
            params['password_change_required'] = password_change_required
        if status is not None:
            params['status'] = status
        if role is not None:
            params['role'] = role
        if subaccount_role is not None:
            params['subaccount_role'] = subaccount_role
        response = self.json_api_call('POST', path, params)
        return response

    def delete_admin(self, admin_id):
        """
        Deletes an administrator.

        admin_id - The id of the administrator.

        Raises RuntimeError on error.
        """
        admin_id = urllib.parse.quote_plus(str(admin_id))
        path = '/admin/v1/admins/%s' % admin_id
        return self.json_api_call('DELETE', path, {})

    def reset_admin(self, admin_id):
        """
        Resets the admin lockout.

        admin_id - <int:admin id>

        Raises RuntimeError on error.
        """
        admin_id = urllib.parse.quote_plus(str(admin_id))
        path = '/admin/v1/admins/%s/reset' % admin_id
        return self.json_api_call('POST', path, {})

    def activate_admin(self, email,
                       send_email=False,
                       valid_days=None,
                       admin_role=None):
        """
        Generates an activation code for an administrator and optionally
        emails the administrator.

        email - <str:email address of administrator>
        valid_days - <int:number of days> (optional)
        send_email - <bool:True if email should be sent> (optional)
        admin_role - <str: Role assigned to new admin> (optional)

        Returns {
            "admin_activation_id": <str:ID of the administrator activation link>
            "admin_role": <str:administrator role assigned to the new admin>
            "code": <str:activation code>
            "email": <str:email for admin/message>
            "email_sent": <string:true if email was sent, false otherwise>
            "expires": <int:timestamp of expiration>
            "link": <str:activation link>
            "message": <str:message in email body>
            "subject": <str:email subject line>
            "valid_days": <int:valid days>

        }

        See the adminapi docs for updated return values.

        Raises RuntimeError on error.
        """
        params = {}
        if email is not None:
            params['email'] = email
        if send_email is not None:
            params['send_email'] = str(send_email)
        if valid_days is not None:
            params['valid_days'] = str(valid_days)
        if admin_role is not None:
            params['admin_role'] = str(admin_role)
        response = self.json_api_call('POST',
                                      '/admin/v1/admins/activations',
                                      params)
        return response

    def get_external_password_mgmt_statuses(self, limit=None, offset=0):
        """
        Returns a paged list of administrators indicating whether they
        have been configured for external password management.
        Args:
            limit: The max number of admins to fetch at once. Default None
            offset: If a limit is passed, the offset to start retrieval.
                    Default 0

        Returns a list of administrators' external password management
            statuses.  See the adminapi docs.

        Raises RuntimeError on error.
        """

        (limit, offset) = self.normalize_paging_args(limit, offset)
        if limit:
            return self.json_api_call(
                'GET',
                '/admin/v1/admins/password_mgmt',
                {'limit': limit, 'offset': offset}
            )

        iterator = self.json_paging_api_call(
            'GET', '/admin/v1/admins/password_mgmt', {})

        return list(iterator)

    def get_external_password_mgmt_status_for_admin(self, admin_id):
        """
        Returns the external password management status for an admin

        admin_id - The id of the admin.

        Returns an external password management status. See the
        adminapi docs.

        Raises RuntimeError on error.
        """

        admin_id = urllib.parse.quote_plus(str(admin_id))
        path = '/admin/v1/admins/{}/password_mgmt'.format(admin_id)
        response = self.json_api_call('GET', path, {})
        return response

    def update_admin_password_mgmt_status(
        self, admin_id, has_external_password_mgmt=None,
        password=None):
        """
        Enable or disable an admin for external password management,
        and optionally set the password for an admin

        admin_id - The id of the admin.
        has_external_password_mgmt - whether or not this admin's password
            is managed via API.
        password - New password for the admin.

        Returns an external password management status. See the
        adminapi docs.

        Raises RuntimeError on error.
        """

        params = {}
        if password is not None:
            params['password'] = password
        if has_external_password_mgmt is not None:
            params['has_external_password_mgmt'] = str(has_external_password_mgmt)

        admin_id = urllib.parse.quote_plus(str(admin_id))
        path = '/admin/v1/admins/{}/password_mgmt'.format(admin_id)
        response = self.json_api_call('POST', path, params)
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
            'logo': base64.b64encode(logo).decode(),
        }
        return self.json_api_call('POST', '/admin/v1/logo', params)

    def delete_logo(self):
        return self.json_api_call('DELETE', '/admin/v1/logo', params={})

    def get_u2ftokens(self, limit=None, offset=0):
        """
        Retrieves a list of u2ftokens
        Args:
            limit: The max number of u2ftokens to fetch at once. Default None
            offset: If a limit is passed, the offset to start retrieval.
                    Default 0

        Returns: A list of u2ftokens

        Notes: Raises RuntimeError on error.
        """
        (limit, offset) = self.normalize_paging_args(limit, offset)

        if limit:
            return self.json_api_call('GET',
                                      '/admin/v1/u2ftokens',
                                      {'limit': limit, 'offset': offset})

        iterator = self.get_u2ftokens_iterator()
        return list(iterator)

    def get_u2ftokens_iterator(self):
        """
        Provides a generator which u2ftokens. Under the hood, this generator
        uses pagination, so it will only store one page of administrative_units
        at a time in memory.

        Returns: A generator which produces u2ftokens.

        Raises RuntimeError on error.
        """
        return self.json_paging_api_call('GET', '/admin/v1/u2ftokens', {})

    def get_webauthncredentials(self, limit=None, offset=0):
        """
        Retrieves a list of webauthn credentials
        Args:
            limit: The max number of webauthn credentials to fetch at once. Default None
            offset: If a limit is passed, the offset to start retrieval.
                    Default 0

        Returns: A list of webauthn credentials

        Notes: Raises RuntimeError on error.
        """
        (limit, offset) = self.normalize_paging_args(limit, offset)

        if limit:
            return self.json_api_call('GET',
                                      '/admin/v1/webauthncredentials',
                                      {'limit': limit, 'offset': offset})

        iterator = self.get_webauthncredentials_iterator()
        return list(iterator)

    def get_webauthncredentials_iterator(self):
        """
        Provides a generator which webauthn credentials. Under the hood, this generator
        uses pagination, so it will only store one page of administrative_units
        at a time in memory.

        Returns: A generator which produces webauthn credentials.

        Raises RuntimeError on error.
        """
        return self.json_paging_api_call('GET', '/admin/v1/webauthncredentials', {})

    def get_u2ftoken_by_id(self, registration_id):
        """ Returns u2ftoken specified by registration_id.

            Params:
                registration_id (str): The registration id of the
                    u2ftoken to fetch.

            Returns:
                A u2ftoken dict.

            Notes:
                Raises RuntimeError on error.
        """
        registration_id = urllib.parse.quote_plus(str(registration_id))
        path = '/admin/v1/u2ftokens/' + registration_id
        response = self.json_api_call('GET', path, {})
        return response

    def delete_u2ftoken(self, registration_id):
        """ Deletes a u2ftoken. If the u2ftoken is already
            deleted, does nothing.

            Params:
                registration_id (str): The registration id of the u2f token.

            Notes:
                Raises RuntimeError on error.
        """
        registration_id = \
            urllib.parse.quote_plus(str(registration_id))
        path = '/admin/v1/u2ftokens/' + registration_id
        return self.json_api_call('DELETE', path, {})

    def get_webauthncredential_by_id(self, webauthnkey):
        """ Returns webauthn credentials specified by webauthnkey.

            Params:
                webauthnkey (str): The registration id of the
                    webauthn credentials to fetch.

            Returns:
                Returns a webauthn credentials dict.

            Notes:
                Raises RuntimeError on error.
        """
        webauthnkey = \
            urllib.parse.quote_plus(str(webauthnkey))
        path = '/admin/v1/webauthncredentials/' + webauthnkey
        response = self.json_api_call('GET', path, {})
        return response

    def delete_webauthncredential(self, webauthnkey):
        """ Deletes a webauthn credentials. If the webauthn credentials is already
            deleted, does nothing.

            Params:
                webauthnkey (str): The registration id of the
                    webauthn credentials.

            Notes:
                Raises RuntimeError on error.
        """
        webauthnkey = \
            urllib.parse.quote_plus(str(webauthnkey))
        path = '/admin/v1/webauthncredentials/' + webauthnkey
        response = self.json_api_call('DELETE', path, {})
        return response

    def get_bypass_codes_generator(self):
        """
        Returns a generator yielding bypass codes.
        """
        return self.json_paging_api_call(
            'GET',
            '/admin/v1/bypass_codes',
            {}
        )

    def get_bypass_codes(self, limit=None, offset=0):
        """
        Retrieves a list of bypass codes.
        Args:
            limit: The max number of admins to fetch at once. Default None
            offset: If a limit is passed, the offset to start retrieval.
                    Default 0

        Returns: list of bypass codes

        Raises RuntimeError on error.

        """
        (limit, offset) = self.normalize_paging_args(limit, offset)
        if limit:
            return self.json_api_call(
                'GET',
                '/admin/v1/bypass_codes',
                {'limit': limit, 'offset': offset}
            )

        return list(self.get_bypass_codes_generator())

    def delete_bypass_code_by_id(self, bypass_code_id):
        """ Deletes a bypass code. If the bypass code is already
            deleted, does nothing.

            Params:
                bypass_code_id (str): The id of the bypass code.

            Notes:
                Raises RuntimeError on error.
        """
        bypass_code_id = \
            urllib.parse.quote_plus(str(bypass_code_id))
        path = '/admin/v1/bypass_codes/' + bypass_code_id
        response = self.json_api_call('DELETE', path, {})
        return response

    def sync_user(self, username, directory_key):
        """ Syncronize a single user immediately with a specified directory.

        Params:
            username (str) - The username of the user to be synchronized.
            directory_key (str) - The unique id of the directory.

        Notes:
            Raises RuntimeError on error.
        """
        params = {
            'username': username,
        }
        directory_key = urllib.parse.quote_plus(directory_key)
        path = (
            '/admin/v1/users/directorysync/{directory_key}/syncuser').format(
                directory_key=directory_key)
        return self.json_api_call('POST', path, params)

    def send_verification_push(self, user_id, phone_id):
        return self.json_api_call(
            'POST',
            f'/admin/v1/users/{user_id}/send_verification_push',
            {'phone_id': phone_id}
        )

    def get_verification_push_response(self, user_id, push_id):
        return self.json_api_call(
            'GET',
            f'/admin/v1/users/{user_id}/verification_push_response',
            {'push_id': push_id},
        )
    def get_trust_monitor_events_iterator(
        self,
        mintime,
        maxtime,
        event_type=None,
    ):
        """
        Returns a generator which yields trust monitor events.

        Params:
            mintime (int) - Return events that have a surfaced timestamp greater
                            than or equal to mintime. Timestamp is represented as
                            a unix timestamp in milliseconds.
            maxtime (int) - Return events that have a surfaced timestamp less
                            than or equal to maxtime. Timestamp is represented as
                            a unix timestamp in milliseconds.
            event_type (str, optional) - Limit the events returned by a supplied
                                         event type represented as a string. If
                                         not supplied, the caller will recieve all
                                         event types. Check the Duo Admin API
                                         documentation for expected values for
                                         this parameter.

        Returns: Generator which yields trust monitor events.
        """

        params = {
            "mintime": "{}".format(mintime),
            "maxtime": "{}".format(maxtime),
        }

        if event_type is not None:
            params["type"] = event_type

        return self.json_cursor_api_call(
            "GET",
            "/admin/v1/trust_monitor/events",
            params,
            lambda resp: resp["events"],
        )

    def get_trust_monitor_events_by_offset(
        self,
        mintime,
        maxtime,
        limit=None,
        offset=None,
        event_type=None,
    ):
        """
        Fetch Duo Trust Monitor Events from the Admin API.

        Params:
            mintime (int) - Return events that have a surfaced timestamp greater
                            than or equal to mintime. Timestamp is represented as
                            a unix timestamp in milliseconds.
            maxtime (int) - Return events that have a surfaced timestamp less
                            than or equal to maxtime. Timestamp is represented as
                            a unix timestamp in milliseconds.
            limit (int, optional) - Limit the number of events returned.
            offset (str, optional) - Provide an offset from a previous request's
                                     response metadata["next_offset"].
            event_type (str, optional) - Limit the events returned by a supplied
                                         event type represented as a string. If
                                         not supplied, the caller will recieve all
                                         event types. Check the Duo Admin API
                                         documentation for expected values for
                                         this parameter.

        Returns: response containing a list of Duo Trust Monitor Events.

        """

        params = {
            "mintime": "{}".format(mintime),
            "maxtime": "{}".format(maxtime),
        }

        if limit is not None:
            params["limit"] = "{}".format(limit)

        if offset is not None:
            params["offset"] = "{}".format(offset)

        if event_type is not None:
            params["type"] = event_type

        return self.json_api_call(
            "GET",
            "/admin/v1/trust_monitor/events",
            params,
        )

    def _quote_policy_id(self, policy_key):
        return urllib.parse.quote_plus("{}".format(policy_key))

    def get_policies_v2_iterator(self):
        """
        Obtain an iterator for retrieving all the policies. The order isn't defined.
        Returns: Iterator of dict elements. Each element contains the policy content.
        """

        return self.json_paging_api_call(
            "GET",
            "/admin/v2/policies",
            {},
        )

    def get_policies_v2(self, limit=None, offset=0):
        """
        Retrieves a list of policies. The order isn't defined.
        Args:
            limit (int, optional): The max number of policies to fetch at once.
            offset (int, optional): If a limit is passed, the offset to start retrieval.
                Default 0
        Raises RuntimeError on error.
        """

        (limit, offset) = self.normalize_paging_args(limit, offset)
        if limit:
            return self.json_api_call(
                "GET",
                "/admin/v2/policies",
                {"limit": limit, "offset": offset},
            )
        return list(self.get_policies_v2_iterator())

    def delete_policy_v2(self, policy_key):
        """
        Deletes a policy.
        Params:
            policy_key (str) - Unique id of the policy
        Notes:
            Raises RuntimeError on error.
        """

        path = "/admin/v2/policies/" + self._quote_policy_id(policy_key)
        return self.json_api_call("DELETE", path, {})

    def update_policy_v2(self, policy_key, json_request):
        """
        Update the content of a single policy
        Args:
            policy_key (str) - Unique id of the policy
            json_request (dict) - policy content to update.
        Returns (dict) - policy after updates have been made.
        """

        path = "/admin/v2/policies/" + self._quote_policy_id(policy_key)
        response = self.json_api_call("PUT", path, json_request)
        return response
    
    def update_policies_v2(self, sections, sections_to_delete, 
                           edit_list, edit_all_policies=False):
        """
        Update the contents of multiple policies.

        Args:
            sections (dict): policy content to update
            sections_to_delete (list): List of section names to delete
            edit_list (list): List of new policy keys to apply the changes to.
                               Ignored if edit_all_policies is True.
            edit_all_policies (bool, optional): Apply changes to all policies.
                                Defaults to False. 
        Returns (list): all updated policies
        """
        path = "/admin/v2/policies/update"
        params = {
            "policies_to_update": {
                "edit_all_policies": edit_all_policies,
                "edit_list": edit_list,
            },
            "policy_changes": {
                "sections": sections,
                "sections_to_delete": sections_to_delete,
            },
        }
        response = self.json_api_call("PUT", path, params)
        return response

    def create_policy_v2(self, json_request):
        """
        Args:
            json_request (dict) - policy content to create.
        Returns (dict) - newly created policy
        """

        path = "/admin/v2/policies"
        response = self.json_api_call("POST", path, json_request)
        return response
    
    def copy_policy_v2(self, policy_key, new_policy_names_list):
        """
        Copy policy to multiple new policies.
 
        Args:
            policy_key (str): Unique id of the policy to copy from
            new_policy_names_list (array): The policy specified by policy_key
                                            will be copied once for each name
                                            in the list
        Returns (list): all new policies
        """
        path = "/admin/v2/policies/copy"
        params = {
            "policy_key": policy_key, 
            "new_policy_names_list": new_policy_names_list
        }
        response = self.json_api_call("POST", path, params)
        return response

    def get_policy_v2(self, policy_key):
        """
        Args:
            policy_key: policy_key (str) - Unique id of the policy
        Returns (dict) - policy content
        """

        path = "/admin/v2/policies/" + self._quote_policy_id(policy_key)
        response = self.json_api_call("GET", path, {})
        return response
    
    def get_policy_summary_v2(self):
        """
        Returns (dict) - summary of all policies and the applications 
        and groups to which they are applied. 
        """

        path = "/admin/v2/policies/summary"
        response = self.json_api_call("GET", path, {})
        return response

    def calculate_policy(self, integration_key, user_id):
        """
        Args:
            integration_key - The integration_key of the application to evaluate. (required)
            user_id - The user_id of the user to evaluate (required)

        Returns (dict) - Dictionary containing "policy_elements" and "sections"
        """

        path = "/admin/v2/policies/calculate"
        response = self.json_api_call(
            "GET",
            path,
            {"integration_key": integration_key, "user_id": user_id},
        )
        return response

    def get_passport_config(self):
        """
        Retrieve the current Passport configuration.

        Returns (dict):
            {
                "enabled_status": string,
                "enabled_groups": [
                    {
                        "group_id": user group ID,
                        "group_name": descriptive user group name,
                        ...
                    },
                    ...
                ]
                "disabled_groups": [
                    {
                        "group_id": user group ID,
                        "group_name": descriptive user group name,
                        ...
                    },
                    ...
                ]
            }
        """

        path = "/admin/v2/passport/config"
        response = self.json_api_call("GET", path, {})
        return response

    def update_passport_config(self, enabled_status, enabled_groups: Optional[List[str]]=None, disabled_groups: Optional[List[str]]=None, custom_supported_browsers=None):
        """
        Update the current Passport configuration.

        Args:
            enabled_status (str) - one of "disabled", "enabled", "enabled-for-groups",
                or "enabled-with-exceptions"
            enabled_groups (list[str]) - if enabled_status is "enabled-for-groups", a
                list of user group IDs for whom Passport should be enabled
            disabled_groups (list[str]) - if enabled_status is "enabled-with-exceptions",
                a list of user group IDs for whom Passport should be disabled
            custom_supported_browsers (dict) - a dict of criteria that determines whether 
                a Windows or macOS browsers should be supported by Passport
        """
        if custom_supported_browsers is None:
            custom_supported_browsers = {"macos": [], "windows": [],}

        path = "/admin/v2/passport/config"
        response = self.json_api_call(
            "POST",
            path,
            {
                "enabled_status": enabled_status,
                "enabled_groups": enabled_groups,
                "disabled_groups": disabled_groups,
                "custom_supported_browsers": custom_supported_browsers,
            },
        )
        return response


class AccountAdmin(Admin):
    """AccountAdmin manages a child account using an Accounts API integration."""

    def __init__(self, account_id, child_api_host=None, **kwargs):
        """Initializes an AccountAdmin for administering a child account.
           account_id is the account id of the child account.
           child_api_host is the api hostname of the child account.
           If this is not provided, this value will be calculated for correct API usage.
           See the Client base class for other parameters.
          """
        if not child_api_host:
            child_api_host =  Accounts.child_map.get(account_id, None)
            if child_api_host is None:
                child_api_host = kwargs.get('host')
                try:
                    child_api_host =  self.get_child_api_host(account_id, **kwargs)
                except RuntimeError:
                    pass
        kwargs['host'] = child_api_host
        
        super(AccountAdmin, self).__init__(**kwargs)
        self.account_id = account_id

    def get_child_api_host(self, account_id, **kwargs):
        accounts_api = Accounts(**kwargs)
        accounts_api.get_child_accounts()
        return Accounts.child_map.get(account_id, kwargs['host'])

    def get_edition(self):
        """
        Returns the edition of the account {
            "edition" : <str:edition name>
        }

        Raises RuntimeError on error.
        """
        response = self.json_api_call('GET',
                                      '/admin/v1/billing/edition',
                                      params={})

        return response

    def set_edition(self, edition):
        """
        Set the edition of the child account.

        edition -  The edition string to set on the child account.
                   Should be 'ENTERPRISE' (MFA), 'PLATFORM' (Access), or 'BEYOND'.

        Raises RuntimeError on error.
        """
        params = {
            'edition': edition,
        }

        return self.json_api_call('POST',
                                  '/admin/v1/billing/edition',
                                  params)

    def get_telephony_credits(self):
        """
        Returns the telephony credits of the account {
            "credits" : <int>
        }

        Raises RuntimeError on error.
        """
        return self.json_api_call('GET',
                                      '/admin/v1/billing/telephony_credits',
                                      params={})


    def set_telephony_credits(self, credits):
        """
        Set the telephony credits of the child account.

        credits -  The telephony credits to set on the child account.
                   The ammount added to the child account,
                   (credits - child's current telephony credits), will be
                   deducted from the parent account's telephony credits.

        Raises RuntimeError on error.
        """
        params = {
            'credits': str(credits),
        }
        return self.json_api_call('POST',
                           '/admin/v1/billing/telephony_credits',
                           params)
