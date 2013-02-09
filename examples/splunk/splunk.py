#!/usr/bin/python
import ConfigParser
import os
import sys
import time

from duo_client import admin


class BaseLog(object):

    def __init__(self, ikey, skey, host, path, logname, ca):
        self.ikey = ikey
        self.skey = skey
        self.host = host
        self.path = path
        self.logname = logname
        self.ca = ca

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
        path = self.path + "/" + self.logname + "_last_timestamp_" + self.host
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
    def __init__(self, ikey, skey, host, path, ca=None):
        BaseLog.__init__(self, ikey, skey, host, path, "administrator",
                         ca=ca)

    def get_events(self):
        self.events = admin.get_administrator_log(self.ikey, self.skey,
            self.host, ca=self.ca, mintime=self.mintime)

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

                #fmtstr = '[%(ctime)s] ' \
            fmtstr = '%(timestamp)s,' \
                     'host="%(host)s", ' \
                     'eventtype="%(eventtype)s", ' \
                     'username="%(username)s", ' \
                     'action="%(actionlabel)s"'
            if event['object']:
                fmtstr += ', object="%(object)s"'
            if event['description']:
                fmtstr += ', description="%(description)s"'

            print fmtstr % event


class AuthenticationLog(BaseLog):
    def __init__(self, ikey, skey, host, path, ca=None):
        BaseLog.__init__(self, ikey, skey, host, path, "authentication", ca)

    def get_events(self):
        self.events = admin.get_authentication_log(self.ikey, self.skey,
            self.host, ca=self.ca, mintime=self.mintime)

    def print_events(self):
        """
        Print events in a format suitable for Splunk.
        """
        for event in self.events:
            event['ctime'] = time.ctime(event['timestamp'])

            #fmtstr = '[%(ctime)s] ' \
            fmtstr = '%(timestamp)s,' \
                     'host="%(host)s", ' \
                     'eventtype="%(eventtype)s", ' \
                     'username="%(username)s", ' \
                     'factor="%(factor)s", ' \
                     'result="%(result)s", ' \
                     'ip="%(ip)s", ' \
                     'integration="%(integration)s"'

            print fmtstr % event


class TelephonyLog(BaseLog):
    def __init__(self, ikey, skey, host, path, ca=None):
        BaseLog.__init__(self, ikey, skey, host, path, "telephony",
                         ca=ca)

    def get_events(self):
        self.events = admin.get_telephony_log(self.ikey, self.skey,
            self.host, ca=self.ca, mintime=self.mintime)

    def print_events(self):
        """
        Print events in a format suitable for Splunk.
        """
        for event in self.events:
            event['ctime'] = time.ctime(event['timestamp'])
            event['host'] = self.host

            #fmtstr = '[%(ctime)s] ' \
            fmtstr = '%(timestamp)s,' \
                     'host="%(host)s", ' \
                     'eventtype="%(eventtype)s", ' \
                     'context="%(context)s", ' \
                     'type="%(type)s", ' \
                     'phone="%(phone)s", ' \
                     'credits="%(credits)s"'

            print fmtstr % event


def get_config(path):
    """
    Returns the configuration parameters stored in config file.

    Returns: (<str:ikey>, <str:skey>, <str:host>, <str:ca path>)
    """
    config = ConfigParser.ConfigParser()
    config.read(path)
    config_d = dict(config.items('duo'))
    ca = config_d.get("ca", None)
    return (config_d['ikey'], config_d['skey'], config_d['host'], ca)


def usage():
    """
        Display usage information and exit.
    """
    progname = os.path.basename(sys.argv[0])
    print >> sys.stderr, "usage: %s [<path>]" % progname
    print >> sys.stderr, "\tpath - path to configuration file"
    sys.exit(1)


def main():
    if len(sys.argv) > 2:
        usage()

    if len(sys.argv) == 1:
        config_path = os.path.abspath(__file__)
        config_path = os.path.dirname(config_path)
        config_path = config_path + "/duo.conf"
    else:
        config_path = os.path.abspath(sys.argv[1])

    ikey, skey, host, ca = get_config(config_path)

    # Use the directory of the config file to store the last event tstamps
    path = os.path.dirname(config_path)

    for logclass in (AdministratorLog, AuthenticationLog, TelephonyLog):
        log = logclass(ikey, skey, host, path, ca)
        log.run()


if __name__ == '__main__':
    main()
