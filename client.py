import os, sys, urllib, hashlib, hmac, base64
import json
from https_wrapper import CertValidatingHTTPSConnection

ca_certs = os.path.join(os.path.dirname(__file__), 'ca_certs.pem')

def canonicalize(method, host, uri, params):
    canon = [method.upper(), host.lower(), uri]

    args = []
    for key in sorted(params.keys()):
        val = params[key]
        arg = '%s=%s' % (urllib.quote(key, '~'), urllib.quote(val, '~'))
        args.append(arg)
    canon.append('&'.join(args))

    return '\n'.join(canon)

def sign(ikey, skey, method, host, uri, params):
    """
    Return basic authorization header line with a Duo Web API signature.
    """
    sig = hmac.new(skey, canonicalize(method, host, uri, params), hashlib.sha1)
    auth = '%s:%s' % (ikey, sig.hexdigest())
    return 'Basic %s' % base64.b64encode(auth)

def call(ikey, skey, host, method, path, **kwargs):
    """
    Call a Duo Web API method and return a (status, reason, data) tuple.
    """
    headers = {'Authorization':sign(ikey, skey, method, host, path, kwargs)}

    if method in [ 'POST', 'PUT' ]:
        headers['Content-type'] = 'application/x-www-form-urlencoded'
        body = urllib.urlencode(kwargs, doseq=True)
        uri = path
    else:
        body = None
        uri = path + '?' + urllib.urlencode(kwargs, doseq=True)

    conn = CertValidatingHTTPSConnection(host, 443, ca_certs=ca_certs)
    conn.request(method, uri, body, headers)
    response = conn.getresponse()
    data = response.read()
    conn.close()

    return (response.status, response.reason, data)

def call_json_api(ikey, skey, host, method, path, **kwargs):
    """
    Call a Duo Web API method which is expected to return a standard JSON
    body with a 200 status.  Return the response element, or raise
    RuntimeError.
    """
    (status, reason, data) = call(ikey, skey, host, method, path, **kwargs)
    if status != 200:
        raise RuntimeError('Received %s %s: %s' % (status, reason, data))
    try:
        data = json.loads(data)
        if data['stat'] != 'OK':
            raise RuntimeError('Received error response: %s' % data)
        return data['response']
    except (ValueError, KeyError):
        raise RuntimeError('Received bad response: %s' % data)

