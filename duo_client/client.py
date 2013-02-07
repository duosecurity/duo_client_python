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
    argparse_error = None
except ImportError as e:
    argparse_error = e

try:
    # Only needed if signing requests with timezones other than UTC.
    import pytz
    pytz_error = None
except ImportError as e:
    pytz_error = e

from https_wrapper import CertValidatingHTTPSConnection

ca_certs = os.path.join(os.path.dirname(__file__), 'ca_certs.pem')


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


def call(ikey, skey, host, method, path, ca=None, sig_version=2,
         sig_timezone='UTC', **kwargs):
    """
    Call a Duo Web API method and return a (status, reason, data) tuple.

    ca - Path to CA pem file.
    """
    # urllib cannot handle unicode strings properly. quote() excepts,
    # and urlencode() replaces them with '?'.
    kwargs = encode_params(kwargs)

    if sig_timezone == 'UTC':
        now = email.utils.formatdate()
    elif pytz_error:
        raise pytz_error
    else:
        d = datetime.datetime.now(pytz.timezone(sig_timezone))
        now = d.strftime("%a, %d %b %Y %H:%M:%S %z")

    auth = sign(ikey, skey, method, host, path, now, sig_version, kwargs)
    headers = {'Authorization': auth, 'Date': now}

    if method in ['POST', 'PUT']:
        headers['Content-type'] = 'application/x-www-form-urlencoded'
        body = urllib.urlencode(kwargs, doseq=True)
        uri = path
    else:
        body = None
        uri = path + '?' + urllib.urlencode(kwargs, doseq=True)

    if ca is None:
        ca = ca_certs

    if ca == 'HTTP':
        conn = httplib.HTTPConnection(host)
    elif ca == 'DISABLE':
        conn = httplib.HTTPSConnection(host, 443)
    else:
        conn = CertValidatingHTTPSConnection(host, 443, ca_certs=ca)
    conn.request(method, uri, body, headers)
    response = conn.getresponse()
    data = response.read()
    conn.close()

    return (response, data)


def call_json_api(ikey, skey, host, method, path, ca=None, sig_version=2,
                  **kwargs):
    """
    Call a Duo Web API method which is expected to return a standard JSON
    body with a 200 status.  Return the response element, or raise
    RuntimeError.
    """
    (response, data) = call(ikey, skey, host, method, path, ca,
                                  sig_version,
                                  **kwargs)
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


def cmd_args():
    """
    Return namespace of args from command invocation.
    """
    if argparse_error:
        raise argparse_error
    parser = argparse.ArgumentParser()
    # named arguments
    parser.add_argument('--ikey', required=True)
    parser.add_argument('--skey', required=True)
    parser.add_argument('--host', required=True)
    parser.add_argument('--method', required=True)
    parser.add_argument('--path', required=True)
    parser.add_argument('--ca')
    parser.add_argument('--sig-version', type=int, default=2)
    parser.add_argument('--sig-timezone', default='UTC')
    parser.add_argument('--show-header', action='append', default=[])
    # optional positional arguments are used for GET/POST params, name=val
    parser.add_argument('param', nargs='*')
    args = parser.parse_args()
    param = collections.defaultdict(list)
    for p in args.param:
        try:
            (k, v) = p.split('=', 1)
        except ValueError:
            sys.exit('Error: Positional argument %s is not '
                     'in key=value format.' % (p,))
        param[k].append(v)
    for (k, v) in param.items():
        if len(v) != 1:
            # Each parameter must have a single value. No Duo API
            # endpoints have arguments that accept multiple values for
            # the same parameter. Thus, the call() and sign() provided
            # here can't handle a list of values for the same
            # parameter.
            raise NotImplementedError
        (v,) = v
        param[k] = v
    del args.param
    for (k, v) in param.items():
        setattr(args, k, v)
    return args


def main():
    args = cmd_args()

    # akgood hack! (I don't particularly like the **kwargs interface
    # in call() FWIW, would rather it explicitly accepted a dict of
    # params...)
    kwargs = vars(args)
    headers = kwargs['show_header']
    del kwargs['show_header']

    (response, data) = call(**kwargs)
    output_response(response, data, headers)

if __name__ == '__main__':
    main()
