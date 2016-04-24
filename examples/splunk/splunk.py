#!/usr/bin/python
from __future__ import absolute_import
from __future__ import print_function
import six.moves.configparser
import optparse
import os
import sys
import time

import duo_client

# For proxy support
from urlparse import urlparse


class BaseLog(object):

    def __init__(self, admin_api, path, logname):
        self.admin_api = admin_api
        self.path = path
        self.logname = logname

        self.mintime = 0
        self.events = []

    def get_events(self):
        raise NotImplementedError

    def print_events(self):
        raise NotImplementedError

    def get_last_timestamp_path(self):
        """
        Returns the path to the file containing the timestamp of the last
        event fetched.
        """
        filename = self.logname + "_last_timestamp_" + self.admin_api.host
        path = os.path.join(self.path, filename)
        return path

    def get_mintime(self):
        """
            Updates self.mintime which is the minimum timestamp of
            log events we want to fetch.
            self.mintime is > all event timestamps we have already fetched.
        """
        try:
            # Only fetch events that come after timestamp of last event
            path = self.get_last_timestamp_path()
            self.mintime = int(open(path).read().strip()) + 1
        except IOError:
            pass

    def write_last_timestamp(self):
        """
            Store last_timestamp so that we don't fetch the same events again
        """
        if not self.events:
            # Do not update last_timestamp
            return

        last_timestamp = 0
        for event in self.events:
            last_timestamp = max(last_timestamp, event['timestamp'])

        path = self.get_last_timestamp_path()
        f = open(path, "w")
        f.write(str(last_timestamp))
        f.close()

    def run(self):
        """
        Fetch new log events and print them.
        """
        self.events = []
        self.get_mintime()
        self.get_events()
        self.print_events()
        self.write_last_timestamp()


class AdministratorLog(BaseLog):
    def __init__(self, admin_api, path):
        BaseLog.__init__(self, admin_api, path, "administrator")

    def get_events(self):
        self.events = self.admin_api.get_administrator_log(
            mintime=self.mintime,
        )

    def print_events(self):
        """
        Print events in a format suitable for Splunk.
        """
        for event in self.events:
            event['ctime'] = time.ctime(event['timestamp'])
            event['actionlabel'] = {
                'admin_login': "Admin Login",
                'admin_create': "Create Admin",
                'admin_update': "Update Admin",
                'admin_delete': "Delete Admin",
                'customer_update': "Update Customer",
                'group_create': "Create Group",
                'group_udpate': "Update Group",
                'group_delete': "Delete Group",
                'integration_create': "Create Integration",
                'integration_update': "Update Integration",
                'integration_delete': "Delete Integration",
                'phone_create': "Create Phone",
                'phone_update': "Update Phone",
                'phone_delete': "Delete Phone",
                'user_create': "Create User",
                'user_update': "Update User",
                'user_delete': "Delete User"}.get(
                event['action'], event['action'])

            fmtstr = '%(timestamp)s,' \
                     'host="%(host)s", ' \
                     'eventtype="%(eventtype)s", ' \
                     'username="%(username)s", ' \
                     'action="%(actionlabel)s"'
            if event['object']:
                fmtstr += ', object="%(object)s"'
            if event['description']:
                fmtstr += ', description="%(description)s"'

            print(fmtstr % event)


class AuthenticationLog(BaseLog):
    def __init__(self, admin_api, path):
        BaseLog.__init__(self, admin_api, path, "authentication")

    def get_events(self):
        self.events = self.admin_api.get_authentication_log(
            mintime=self.mintime,
        )

    def print_events(self):
        """
        Print events in a format suitable for Splunk.
        """
        for event in self.events:
            event['ctime'] = time.ctime(event['timestamp'])

            fmtstr = (
                '%(timestamp)s,'
                'host="%(host)s", '
                'eventtype="%(eventtype)s", '
                'username="%(username)s", '
                'factor="%(factor)s", '
                'result="%(result)s", '
                'reason="%(reason)s", '
                'ip="%(ip)s", '
                'integration="%(integration)s", '
                'newenrollment="%(new_enrollment)s"'
            )

            print(fmtstr % event)


class TelephonyLog(BaseLog):
    def __init__(self, admin_api, path):
        BaseLog.__init__(self, admin_api, path, "telephony")

    def get_events(self):
        self.events = self.admin_api.get_telephony_log(
            mintime=self.mintime,
        )

    def print_events(self):
        """
        Print events in a format suitable for Splunk.
        """
        for event in self.events:
            event['ctime'] = time.ctime(event['timestamp'])
            event['host'] = self.admin_api.host

            fmtstr = '%(timestamp)s,' \
                     'host="%(host)s", ' \
                     'eventtype="%(eventtype)s", ' \
                     'context="%(context)s", ' \
                     'type="%(type)s", ' \
                     'phone="%(phone)s", ' \
                     'credits="%(credits)s"'

            print(fmtstr % event)


def admin_api_from_config(config_path):
    """
    Return a duo_client.Admin object created using the parameters
    stored in a config file.
    """
    config = six.moves.configparser.ConfigParser()
    config.read(config_path)
    config_d = dict(config.items('duo'))
    ca_certs = config_d.get("ca_certs", None)
    if ca_certs is None:
        ca_certs = config_d.get("ca", None)

    ret = duo_client.Admin(
        ikey=config_d['ikey'],
        skey=config_d['skey'],
        host=config_d['host'],
        ca_certs=ca_certs,
    )

    http_proxy = config_d.get("http_proxy", None)
    if http_proxy is not None:
        proxy_parsed = urlparse(http_proxy)
        proxy_host = proxy_parsed.hostname
        proxy_port = proxy_parsed.port
        ret.set_proxy(host = proxy_host, port = proxy_port)

    return ret


def main():
    parser = optparse.OptionParser(usage="%prog [<config file path>]")
    (options, args) = parser.parse_args(sys.argv[1:])

    if len(sys.argv) == 1:
        config_path = os.path.abspath(__file__)
        config_path = os.path.dirname(config_path)
        config_path = os.path.join(config_path, "duo.conf")
    else:
        config_path = os.path.abspath(sys.argv[1])

    admin_api = admin_api_from_config(config_path)

    # Use the directory of the config file to store the last event tstamps
    path = os.path.dirname(config_path)

    for logclass in (AdministratorLog, AuthenticationLog, TelephonyLog):
        log = logclass(admin_api, path)
        log.run()


if __name__ == '__main__':
    main()
