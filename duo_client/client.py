"""
Low level functions for generating Duo Web API calls and parsing results.
"""

import base64
import collections
import copy
import datetime
import email.utils
import hashlib
import hmac
import httplib
import json
import os
import sys
import urllib

try:
    # For the optional demonstration CLI program.
    import argparse
except ImportError as e:
    argparse_error = e
    argparse = None

try:
    # Only needed if signing requests with timezones other than UTC.
    import pytz
except ImportError as e:
    pytz_error = e

from https_wrapper import CertValidatingHTTPSConnection

DEFAULT_CA_CERTS = os.path.join(os.path.dirname(__file__), 'ca_certs.pem')


def canon_params(params):
    args = []
    for key in sorted(params.keys()):
        val = params[key]
        arg = '%s=%s' % (urllib.quote(key, '~'), urllib.quote(val, '~'))
        args.append(arg)
    return '&'.join(args)


def canonicalize(method, host, uri, params, date, sig_version):
    if sig_version == 1:
        canon = []
    elif sig_version == 2:
        canon = [date]
    else:
        raise NotImplementedError(sig_version)

    canon += [
        method.upper(),
        host.lower(),
        uri,
        canon_params(params),
    ]
    return '\n'.join(canon)


def sign(ikey, skey, method, host, uri, date, sig_version, params):
    """
    Return basic authorization header line with a Duo Web API signature.
    """
    canonical = canonicalize(method, host, uri, params, date, sig_version)
    if isinstance(skey, unicode):
        skey = skey.encode('utf-8')
    sig = hmac.new(skey, canonical, hashlib.sha1)
    auth = '%s:%s' % (ikey, sig.hexdigest())
    return 'Basic %s' % base64.b64encode(auth)


def encode_params(params):
    """Returns copy of params with unicode strings utf-8 encoded"""
    new_params = {}
    for key, value in params.items():
        if isinstance(key, unicode):
            key = key.encode("utf-8")
        if isinstance(value, unicode):
            value = value.encode("utf-8")
        new_params[key] = value
    return new_params


class Client(object):
    sig_version = 2

    def __init__(self, ikey, skey, host,
                 ca_certs=DEFAULT_CA_CERTS,
                 sig_timezone='UTC'):
        """
        ca - Path to CA pem file.
        """
        self.ikey = ikey
        self.skey = skey
        self.host = host
        self.sig_timezone = sig_timezone
        if ca_certs is None:
            ca_certs = DEFAULT_CA_CERTS
        self.ca_certs = ca_certs
        self.set_proxy(host=None, proxy_type=None)

    def set_proxy(self, host, port=None, headers=None,
                  proxy_type='CONNECT'):
        """
        Configure proxy for API calls. Supported proxy_type values:

        'CONNECT' - HTTP proxy with CONNECT.
        None - Disable proxy.
        """
        if proxy_type not in ('CONNECT', None):
            raise NotImplementedError('proxy_type=%s' % (proxy_type,))
        self.proxy_headers = headers
        self.proxy_host = host
        self.proxy_port = port
        self.proxy_type = proxy_type

    def api_call(self, method, path, params):
        """
        Call a Duo API method. Return a (status, reason, data) tuple.
        """
        # urllib cannot handle unicode strings properly. quote() excepts,
        # and urlencode() replaces them with '?'.
        params = encode_params(params)

        if self.sig_timezone == 'UTC':
            now = email.utils.formatdate()
        elif pytz is None:
            raise pytz_error
        else:
            d = datetime.datetime.now(pytz.timezone(self.sig_timezone))
            now = d.strftime("%a, %d %b %Y %H:%M:%S %z")

        auth = sign(self.ikey,
                    self.skey,
                    method,
                    self.host,
                    path,
                    now,
                    self.sig_version,
                    params)
        headers = {
            'Authorization': auth,
            'Date': now,
        }

        if method in ['POST', 'PUT']:
            headers['Content-type'] = 'application/x-www-form-urlencoded'
            body = urllib.urlencode(params, doseq=True)
            uri = path
        else:
            body = None
            uri = path + '?' + urllib.urlencode(params, doseq=True)

        # Host and port for the HTTP(S) connection to the API server.
        if self.ca_certs == 'HTTP':
            api_port = 80
            api_proto = 'http'
        else:
            api_port = 443
            api_proto = 'https'

        # Host and port for outer HTTP(S) connection if proxied.
        if self.proxy_type is None:
            host = self.host
            port = api_port
        elif self.proxy_type == 'CONNECT':
            host = self.proxy_host
            port = self.proxy_port
        else:
            raise NotImplementedError('proxy_type=%s' % (self.proxy_type,))

        # Create outer HTTP(S) connection.
        if self.ca_certs == 'HTTP':
            conn = httplib.HTTPConnection(host, port)
        elif self.ca_certs == 'DISABLE':
            conn = httplib.HTTPSConnection(host, port)
        else:
            conn = CertValidatingHTTPSConnection(host,
                                                 port,
                                                 ca_certs=self.ca_certs)

        # Configure CONNECT proxy tunnel, if any.
        if self.proxy_type == 'CONNECT':
            # Ensure the request has the correct Host.
            uri = ''.join((api_proto, '://', self.host, uri))
            if hasattr(conn, 'set_tunnel'): # 2.7+
                conn.set_tunnel(self.host,
                                api_port,
                                self.proxy_headers)
            elif hasattr(conn, '_set_tunnel'): # 2.6.3+
                # pylint: disable=E1103
                conn._set_tunnel(self.host,
                                 api_port,
                                 self.proxy_headers)
                # pylint: enable=E1103

        conn.request(method, uri, body, headers)
        response = conn.getresponse()
        data = response.read()
        conn.close()

        return (response, data)

    def json_api_call(self, method, path, params):
        """
        Call a Duo API method which is expected to return a JSON body
        with a 200 status. Return the response data structure or raise
        RuntimeError.
        """
        (response, data) = self.api_call(method, path, params)
        return self.parse_json_response(response, data)

    def parse_json_response(self, response, data):
        """
        Return the parsed data structure or raise RuntimeError.
        """
        if response.status != 200:
            msg = 'Received %s %s' % (response.status, response.reason)
            try:
                data = json.loads(data)
                if data['stat'] == 'FAIL':
                    if 'message_detail' in data:
                        msg = 'Received %s %s (%s)' % (
                            response.status,
                            data['message'],
                            data['message_detail'],
                        )
                    else:
                        msg = 'Received %s %s' % (
                            response.status,
                            data['message'],
                        )
            except (ValueError, KeyError, TypeError):
                pass
            error = RuntimeError(msg)
            error.status = response.status
            error.reason = response.reason
            error.data = data
            raise error
        try:
            data = json.loads(data)
            if data['stat'] != 'OK':
                raise RuntimeError('Received error response: %s' % data)
            return data['response']
        except (ValueError, KeyError, TypeError):
            raise RuntimeError('Received bad response: %s' % data)


def output_response(response, data, headers=[]):
    """
    Print response, parsed, sorted, and pretty-printed if JSON
    """
    print response.status, response.reason
    for header in headers:
        val = response.getheader(header)
        if val is not None:
            print '%s: %s' % (header, val)
    try:
        data = json.loads(data)
        data = json.dumps(data, sort_keys=True, indent=4)
    except ValueError:
        pass
    print data


def main():
    if argparse is None:
        raise argparse_error
    parser = argparse.ArgumentParser()
    # named arguments
    parser.add_argument('--ikey', required=True,
                        help='Duo integration key')
    parser.add_argument('--skey', required=True,
                        help='Duo integration secret key')
    parser.add_argument('--host', required=True,
                        help='Duo API hostname')
    parser.add_argument('--method', required=True,
                        help='HTTP request method')
    parser.add_argument('--path', required=True,
                        help='API endpoint path')
    parser.add_argument('--ca', default=DEFAULT_CA_CERTS)
    parser.add_argument('--sig-version', type=int, default=2)
    parser.add_argument('--sig-timezone', default='UTC')
    parser.add_argument(
        '--show-header',
        action='append',
        default=[],
        metavar='Header-Name',
        help='Show specified response header(s) (default: only output body).',
    )
    parser.add_argument('--file-args', default=[])
    # optional positional arguments are used for GET/POST params, name=val
    parser.add_argument('param', nargs='*')
    args = parser.parse_args()

    client = Client(
        ikey=args.ikey,
        skey=args.skey,
        host=args.host,
        ca_certs=args.ca,
        sig_timezone=args.sig_timezone,
    )
    client.sig_version = args.sig_version

    params = collections.defaultdict(list)
    for p in args.param:
        try:
            (k, v) = p.split('=', 1)
        except ValueError:
            sys.exit('Error: Positional argument %s is not '
                     'in key=value format.' % (p,))
        params[k].append(v)

    # parse which arguments are filenames
    file_args = args.file_args
    if args.file_args:
        file_args = file_args.split(',')

    for (k, v) in params.items():
        if len(v) != 1:
            # Each parameter must have a single value. No Duo API
            # endpoints have arguments that accept multiple values for
            # the same parameter. Thus, the call() and sign() provided
            # here can't handle a list of values for the same
            # parameter.
            raise NotImplementedError
        (v,) = v
        if k in file_args:      # value is a filename, replace with contents
            with open(v, 'rb') as val:
                params[k] = base64.b64encode(val.read())
        else:
            params[k] = v

    (response, data) = client.api_call(args.method, args.path, params)
    output_response(response, data, args.show_header)

if __name__ == '__main__':
    main()
