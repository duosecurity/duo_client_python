"""
Low level functions for generating Duo Web API calls and parsing results.
"""
__version__ = '5.5.0'

import base64
import collections
import datetime
import email.utils
import hashlib
import hmac
import http.client
import json
import os
import random
from time import sleep
import socket
import ssl
import sys
import urllib.parse

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
    pytz = None
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
        (urllib.parse.quote(key, '~'), vals) for (key, vals) in list(params.items())):
        for val in sorted(urllib.parse.quote(val, '~') for val in vals):
            args.append('%s=%s' % (key, val))
    return '&'.join(args)


def canon_x_duo_headers(additional_headers):
    """
    Args:
        additional_headers: Dict
    Returns:
        stringified version of all headers that start with 'X-Duo*'. Which is then hashed.
        Note: the keys are also lower-cased for signing.
    """
    if additional_headers is None:
        additional_headers = {}

    # Lower the headers before sorting them
    lowered_headers = {}
    for header_name, header_value in additional_headers.items():
        header_name = header_name.lower() if header_name is not None else None
        lowered_headers[header_name] = header_value

    canon_list = []
    added_headers = []  # store headers we've added, use for duplicate checking (case insensitive)
    for header_name in sorted(lowered_headers.keys()):
        # Extract header value and set key to lower case from now on.
        value = lowered_headers[header_name]

        # Validation gate. We will raise if a problem is found here.
        _validate_additional_header(header_name, value, added_headers)

        # Add to the list of values to canonicalize:
        canon_list.extend([header_name, value])
        added_headers.append(header_name)

    canon = '\x00'.join(canon_list)
    return hashlib.sha512(canon.encode('utf-8')).hexdigest()


def _validate_additional_header(header_name, value, added_headers):
    """
    Args:
        header_name: str
        value: str
        added_headers: list[str] - headers we've already added - check for duplicates (case insensitive)
    Returns: None

    Validates additional headers added to request - headers must comply with the following rules (for V5 sig_version)
    """
    if header_name is None or value is None:
        raise ValueError("Not allowed 'None' as a header name or value")
    if '\x00' in header_name:
        raise ValueError("Not allowed 'Null' character in header name")
    if '\x00' in value:
        raise ValueError("Not allowed 'Null' character in header value")
    if not header_name.lower().startswith('x-duo-'):
        raise ValueError("Additional headers must start with \'X-Duo-\'")
    if header_name.lower() in added_headers:
        raise ValueError("Duplicate header passed, header={}".format(header_name))


def canonicalize(method, host, uri, params, date, sig_version, body=None, additional_headers=None):
    """
    Return a canonical string version of the given request attributes.

    * method: string HTTP method
    * host: string hostname
    * uri: string uri path
    * params: string containing request params
    * date: date string for request
    * sig_version: signature version integer
    * body: request body, must be string for sig_version 4
    """
    if sig_version == 1:
        canon = [
            method.upper(),
            host.lower(),
            uri,
            canon_params(params),
        ]
    elif sig_version == 2:
        canon = [
            date,
            method.upper(),
            host.lower(),
            uri,
            canon_params(params),
        ]
    elif sig_version == 4:
        # sig_version 4 is json only
        canon = [
            date,
            method.upper(),
            host.lower(),
            uri,
            canon_params(params),
            hashlib.sha512(body.encode('utf-8')).hexdigest(),
        ]
    elif sig_version == 5:
        canon = [
            date,
            method.upper(),
            host.lower(),
            uri,
            canon_params(params),
            hashlib.sha512(body.encode('utf-8')).hexdigest(),
            canon_x_duo_headers(additional_headers),  # hashed in canon_x_duo_headers
        ]
    else:
        raise ValueError("Unknown signature version: {}".format(sig_version))
    return '\n'.join(canon)


def sign(ikey, skey, method, host, uri, date, sig_version, params, body=None,
         digestmod=hashlib.sha512, additional_headers=None):
    """
    Return basic authorization header line with a Duo Web API signature.
    """
    canonical = canonicalize(method, host, uri, params, date, sig_version, body=body, additional_headers=additional_headers)
    if isinstance(skey, str):
        skey = skey.encode('utf-8')
    if isinstance(canonical, str):
        canonical = canonical.encode('utf-8')

    sig = hmac.new(skey, canonical, digestmod)
    auth = '%s:%s' % (ikey, sig.hexdigest())

    if isinstance(auth, str):
        auth = auth.encode('utf-8')
    b64 = base64.b64encode(auth)
    if not isinstance(b64, str):
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
        if isinstance(value, bool):
            if value:
                value = 'true'
            else:
                value = 'false'
        elif isinstance(value, int):
            value = str(value)
        if isinstance(value, str):
            return value.encode("utf-8")
        return value
    def to_list(value):
        if value is None or isinstance(value, str):
            return [value]
        return value
    return dict(
        (encode(key), [encode(v) for v in to_list(value)])
        for (key, value) in list(params.items()))


class Client(object):
    sig_version = 5

    def __init__(self, ikey, skey, host,
                 ca_certs=DEFAULT_CA_CERTS,
                 sig_timezone='UTC',
                 user_agent=('Duo API Python/' + __version__),
                 timeout=socket._GLOBAL_DEFAULT_TIMEOUT,
                 paging_limit=100,
                 digestmod=hashlib.sha512,
                 sig_version=None,
                 port=None
                 ):
        """
        ca_certs - Path to CA pem file.
        """
        self.ikey = ikey
        self.skey = skey
        self.host = host
        self.port = port
        self.sig_timezone = sig_timezone
        if ca_certs is None:
            ca_certs = DEFAULT_CA_CERTS
        self.ca_certs = ca_certs
        self.user_agent = user_agent
        self.set_proxy(host=None, proxy_type=None)
        self.paging_limit = paging_limit
        self.digestmod = digestmod
        if sig_version is not None:
            self.sig_version = sig_version

        # Constants for handling rate limit backoff and retries
        self._MAX_BACKOFF_WAIT_SECS = 32
        self._INITIAL_BACKOFF_WAIT_SECS = 1
        self._BACKOFF_FACTOR = 2
        self._RATE_LIMITED_RESP_CODE = 429

        # Default timeout is a sentinel object
        if timeout is socket._GLOBAL_DEFAULT_TIMEOUT:
            self.timeout = timeout
        else:
            self.timeout = float(timeout)

        if sig_version == 3:
            raise ValueError('sig_version 3 not supported')

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

    def api_call(
        self,
        method,
        path,
        params,
        additional_headers=None,
        sig_version=None,
    ):
        """
        Call a Duo API method. Return a (response, data) tuple.

        * method: HTTP request method. E.g. "GET", "POST", or "DELETE".
        * path: Full path of the API endpoint. E.g. "/auth/v2/ping".
        * params: dict mapping from parameter name to stringified value,
            or a dict to be converted to json.
        * sig_version: signature version integer
        """
        params_go_in_body = method in ('POST', 'PUT', 'PATCH')
        digestmod = self.digestmod
        if additional_headers is None:
            additional_headers = {}
        if sig_version is None:
            sig_version = self.sig_version

        if sig_version in (1, 2):
            params = normalize_params(params)
            # v1 and v2 canonicalization don't distinguish between
            # params and body. There's no separate body input.
            body = None
        elif sig_version in (4, 5):
            digestmod = hashlib.sha512
            if params_go_in_body:
                body = self.canon_json(params)
                params = {}
            else:
                body = ''
                params = normalize_params(params)
        else:
            raise ValueError('unsupported sig_version {}'.format(sig_version))

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
                    sig_version,
                    params,
                    body=body,
                    digestmod=digestmod,
                    additional_headers=additional_headers)
        headers = {
            'Authorization': auth,
            'Date': now,
        }

        if sig_version == 5:
            for k, v in additional_headers.items():
                headers[k] = v

        if self.user_agent:
            headers['User-Agent'] = self.user_agent

        if params_go_in_body:
            if sig_version in (4, 5):
                headers['Content-type'] = 'application/json'
            else:
                headers['Content-type'] = 'application/x-www-form-urlencoded'
                body = urllib.parse.urlencode(params, doseq=True)
            uri = path
        else:
            body = None
            uri = path + '?' + urllib.parse.urlencode(params, doseq=True)

        encoded_headers = {}
        for k, v in headers.items():
            if isinstance(k, str):
                k = k.encode('ascii')
            if isinstance(v, str):
                v = v.encode('ascii')
            encoded_headers[k] = v

        return self._make_request(method, uri, body, encoded_headers)

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
            conn = http.client.HTTPConnection(host, port)
        elif self.ca_certs == 'DISABLE':
            kwargs = {}
            if hasattr(ssl, '_create_unverified_context'):
                # httplib.HTTPSConnection validates certificates by
                # default in Python 2.7.9+.
                kwargs['context'] = ssl._create_unverified_context()  # noqa: DUO122, explicitly disabled for testing scenarios
            conn = http.client.HTTPSConnection(host, port, **kwargs)
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
        if self.proxy_type == 'CONNECT':
            # Ensure the request uses the correct protocol and Host.
            if self.ca_certs == 'HTTP':
                api_proto = 'http'
            else:
                api_proto = 'https'
            uri = ''.join((api_proto, '://', self.host, uri))
        conn = self._connect()

        # backoff on rate limited requests and retry. if a request is rate
        # limited after MAX_BACKOFF_WAIT_SECS, return the rate limited response
        wait_secs = self._INITIAL_BACKOFF_WAIT_SECS
        while True:
            response, data = self._attempt_single_request(
                conn, method, uri, body, headers)
            if (response.status != self._RATE_LIMITED_RESP_CODE or
                    wait_secs > self._MAX_BACKOFF_WAIT_SECS):
                break
            random_offset = random.uniform(0.0, 1.0)  # noqa: DUO102, non-cryptographic random use
            sleep(wait_secs + random_offset)
            wait_secs = wait_secs * self._BACKOFF_FACTOR

        self._disconnect(conn)
        return (response, data)

    def _attempt_single_request(self, conn, method, uri, body, headers):
        conn.request(method, uri, body, headers)
        response = conn.getresponse()
        data = response.read()
        return (response, data)

    def _disconnect(self, conn):
        conn.close()

    def normalize_paging_args(self, limit=None, offset=0):
        """
        Converts paging arguments to a format the rest of the client expects.

        :param limit: The number of objects requested of a paginated api
                      endpoint. If it looks falsy, it is is not changed.
                      Default None
        :param offset: The offset to start retrieval. Default 0
        :return: tuple after the form of (limit, offset)
        """

        if limit:
            limit = '{}'.format(limit)

        offset = '{}'.format(offset)

        return (limit, offset)

    def json_api_call(self, method, path, params):
        """
        Call a Duo API method which is expected to return a JSON body
        with a 200 status. Return the response data structure or raise
        RuntimeError.
        """
        (response, data) = self.api_call(method, path, params)
        return self.parse_json_response(response, data)

    def json_paging_api_call(self, method, path, params):
        """
        Call a Duo API method which is expected to return a JSON body
        with a 200 status. Return a generator that can be used to get
        response data or raise a RuntimeError.
        """
        objects = []
        next_offset = 0

        if 'limit' not in params and self.paging_limit:
            params['limit'] = str(self.paging_limit)

        while next_offset is not None:
            params['offset'] = str(next_offset)
            (response, data) = self.api_call(method, path, params)
            (objects, metadata) = self.parse_json_response_and_metadata(response, data)
            next_offset = metadata.get('next_offset', None)
            for obj in objects:
                yield obj

    def json_cursor_api_call(self, method, path, params, get_records_func):
        """
        Call a Duo API endpoint which utilizes a cursor in some responses to
        page through a set of data. This cursor is supplied through the optional
        "offset" parameter.  The cursor for the next set of data is in the
        response metadata as "next_offset". Callers must also include a
        function parameter to extract the iterable of records to yield. This is
        slightly different than json_paging_api_call because the first request
        does not contain the offset parameter.

        :param method: The method to make the request w/ as a string. Ex:
                       "GET", "POST", "PUT" etc.
        :param path: The path to make the request with as a string.
        :param params: The dict of parameters to send in the request.
        :param get_records_func: Function that can be called to extract an
                                 iterable of records from the parsed response
                                 json.

        :returns: Generator which will yield records from the api response(s).
        """

        next_offset = None

        if 'limit' not in params and self.paging_limit:
            params['limit'] = str(self.paging_limit)

        while True:
            if next_offset is not None:
                params['offset'] = str(next_offset)
            (http_resp, http_resp_data) = self.api_call(method, path, params)
            (response, metadata) = self.parse_json_response_and_metadata(
                http_resp,
                http_resp_data,
            )
            for record in get_records_func(response):
                yield record
            next_offset = metadata.get('next_offset', None)
            if next_offset is None:
                break

    def parse_json_response(self, response, data):
        """
        Return the parsed data structure or raise RuntimeError.
        """
        (response, metadata) = self.parse_json_response_and_metadata(response, data)

        return response

    def parse_json_response_and_metadata(self, response, data):
        """
        Return the parsed data structure and metadata as a tuple or raise RuntimeError.
        """
        def raise_error(msg):
            error = RuntimeError(msg)
            error.status = response.status
            error.reason = response.reason
            error.data = data
            raise error
        if not isinstance(data, str):
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
            response = data['response']
            metadata = data.get('metadata', {})
            if not metadata and isinstance(response, dict):
                metadata = response.get('metadata', {})

            return (response, metadata)
        except (ValueError, KeyError, TypeError):
            raise_error('Received bad response: %s' % data)

    @classmethod
    def canon_json(cls, params):
        if not isinstance(params, dict):
            raise ValueError('JSON request must be an object.')
        return json.dumps(params, sort_keys=True, separators=(',', ':'))


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
        if not isinstance(data, str):
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
        sig_version=args.sig_version,
        sig_timezone=args.sig_timezone,
    )

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
