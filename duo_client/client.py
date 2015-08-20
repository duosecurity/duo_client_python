"""
Low level functions for generating Duo Web API calls and parsing results.
"""
from __future__ import absolute_import
from __future__ import print_function
import six
__version__ = '3.0'

import base64
import collections
import copy
import datetime
import email.utils
import hashlib
import hmac
import json
import os
import socket
import ssl
import sys

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

from .https_wrapper import CertValidatingHTTPSConnection

DEFAULT_CA_CERTS = os.path.join(os.path.dirname(__file__), 'ca_certs.pem')


def canon_params(params):
    """
    Return a canonical string version of the given request parameters.
    """
    # this is normalized the same as for OAuth 1.0,
    # http://tools.ietf.org/html/rfc5849#section-3.4.1.3.2
    args = []
    for (key, vals) in sorted(
        (six.moves.urllib.parse.quote(key, '~'), vals) for (key, vals) in list(params.items())):
        for val in sorted(six.moves.urllib.parse.quote(val, '~') for val in vals):
            args.append('%s=%s' % (key, val))
    return '&'.join(args)


def canonicalize(method, host, uri, params, date, sig_version):
    """
    Return a canonical string version of the given request attributes.
    """
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
    if isinstance(skey, six.text_type):
        skey = skey.encode('utf-8')
    if isinstance(canonical, six.text_type):
        canonical = canonical.encode('utf-8')
    sig = hmac.new(skey, canonical, hashlib.sha1)
    auth = '%s:%s' % (ikey, sig.hexdigest())
    if isinstance(auth, six.text_type):
        auth = auth.encode('utf-8')
    b64 = base64.b64encode(auth)
    if not isinstance(b64, six.text_type):
        b64 = b64.decode('utf-8')
    return 'Basic %s' % b64


def normalize_params(params):
    """
    Return copy of params with strings listified
    and unicode strings utf-8 encoded.
    """
    # urllib cannot handle unicode strings properly. quote() excepts,
    # and urlencode() replaces them with '?'.
    def encode(value):
        if isinstance(value, six.text_type):
            return value.encode("utf-8")
        return value
    def to_list(value):
        if value is None or isinstance(value, six.string_types):
            return [value]
        return value
    return dict(
        (encode(key), [encode(v) for v in to_list(value)])
        for (key, value) in list(params.items()))


class Client(object):
    sig_version = 2

    def __init__(self, ikey, skey, host,
                 ca_certs=DEFAULT_CA_CERTS,
                 sig_timezone='UTC',
                 user_agent=('Duo API Python/' + __version__),
                 timeout=socket._GLOBAL_DEFAULT_TIMEOUT):
        """
        ca_certs - Path to CA pem file.
        """
        self.ikey = ikey
        self.skey = skey
        self.host = host
        self.port = None
        self.sig_timezone = sig_timezone
        if ca_certs is None:
            ca_certs = DEFAULT_CA_CERTS
        self.ca_certs = ca_certs
        self.user_agent = user_agent
        self.set_proxy(host=None, proxy_type=None)

        # Default timeout is a sentinel object
        if timeout is socket._GLOBAL_DEFAULT_TIMEOUT:
            self.timeout = timeout
        else:
            self.timeout = float(timeout)

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
        Call a Duo API method. Return a (response, data) tuple.

        * method: HTTP request method. E.g. "GET", "POST", or "DELETE".
        * path: Full path of the API endpoint. E.g. "/auth/v2/ping".
        * params: dict mapping from parameter name to stringified value.
        """
        params = normalize_params(params)

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
            'Host': self.host,
        }

        if self.user_agent:
            headers['User-Agent'] = self.user_agent

        if method in ['POST', 'PUT']:
            headers['Content-type'] = 'application/x-www-form-urlencoded'
            body = six.moves.urllib.parse.urlencode(params, doseq=True)
            uri = path
        else:
            body = None
            uri = path + '?' + six.moves.urllib.parse.urlencode(params, doseq=True)

        return self._make_request(method, uri, body, headers)

    def _connect(self):
        # Host and port for the HTTP(S) connection to the API server.
        if self.ca_certs == 'HTTP':
            api_port = 80
        else:
            api_port = 443
        if self.port is not None:
            api_port = self.port

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
            conn = six.moves.http_client.HTTPConnection(host, port)
        elif self.ca_certs == 'DISABLE':
            kwargs = {}
            if hasattr(ssl, '_create_unverified_context'):
                # httplib.HTTPSConnection validates certificates by
                # default in Python 2.7.9+.
                kwargs['context'] = ssl._create_unverified_context()
            conn = six.moves.http_client.HTTPSConnection(host, port, **kwargs)
        else:
            conn = CertValidatingHTTPSConnection(host,
                                                 port,
                                                 ca_certs=self.ca_certs)

        # Override default socket timeout if requested.
        conn.timeout = self.timeout

        # Configure CONNECT proxy tunnel, if any.
        if self.proxy_type == 'CONNECT':
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

        return conn

    def _make_request(self, method, uri, body, headers):
        conn = self._connect()
        if self.proxy_type == 'CONNECT':
            # Ensure the request uses the correct protocol and Host.
            if self.ca_certs == 'HTTP':
                api_proto = 'http'
            else:
                api_proto = 'https'
            uri = ''.join((api_proto, '://', self.host, uri))
        conn.request(method, uri, body, headers)
        response = conn.getresponse()
        data = response.read()
        self._disconnect(conn)
        return (response, data)

    def _disconnect(self, conn):
        conn.close()

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
        def raise_error(msg):
            error = RuntimeError(msg)
            error.status = response.status
            error.reason = response.reason
            error.data = data
            raise error
        if not isinstance(data, six.text_type):
            data = data.decode('utf-8')
        if response.status != 200:
            try:
                data = json.loads(data)
                if data['stat'] == 'FAIL':
                    if 'message_detail' in data:
                        raise_error('Received %s %s (%s)' % (
                            response.status,
                            data['message'],
                            data['message_detail'],
                        ))
                    else:
                        raise_error('Received %s %s' % (
                                response.status,
                            data['message'],
                        ))
            except (ValueError, KeyError, TypeError):
                pass
            raise_error('Received %s %s' % (
                    response.status,
                    response.reason,
            ))
        try:
            data = json.loads(data)
            if data['stat'] != 'OK':
                raise_error('Received error response: %s' % data)
            return data['response']
        except (ValueError, KeyError, TypeError):
            raise_error('Received bad response: %s' % data)


def output_response(response, data, headers=None):
    """
    Print response, parsed, sorted, and pretty-printed if JSON
    """
    if not headers:
        headers = []
    print(response.status, response.reason)
    for header in headers:
        val = response.getheader(header)
        if val is not None:
            print('%s: %s' % (header, val))
    try:
        if not isinstance(data, six.text_type):
            data = data.decode('utf-8')
        data = json.loads(data)
        data = json.dumps(data, sort_keys=True, indent=4)
    except ValueError:
        pass
    print(data)


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

    for (k, v) in list(params.items()):
        if k in file_args:      # value is a filename, replace with contents
            if len(v) != 1:
                # file arguments cannot have multiple values
                raise NotImplementedError
            (v,) = v
            with open(v, 'rb') as val:
                params[k] = base64.b64encode(val.read())
        else:
            params[k] = v

    (response, data) = client.api_call(args.method, args.path, params)
    output_response(response, data, args.show_header)

if __name__ == '__main__':
    main()
