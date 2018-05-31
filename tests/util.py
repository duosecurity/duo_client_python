from __future__ import absolute_import
import json
import collections

from json import JSONEncoder
import duo_client
import six

class MockObjectJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        return getattr(obj.__class__, "to_json")(obj)

# put params in a dict to avoid inconsistent ordering
def params_to_dict(param_str):
    param_dict = collections.defaultdict(list)
    for (key, val) in (param.split('=') for param in param_str.split('&')):
        param_dict[key].append(val)
    return param_dict


class MockHTTPConnection(object):
    """
    Mock HTTP(S) connection that returns a dummy JSON response.
    """
    status = 200            # success!

    def __init__(self, data_response_should_be_list=False):
        # if a response object should be a list rather than
        # a dict, then set this flag to true
        self.data_response_should_be_list = data_response_should_be_list

    def dummy(self):
        return self

    _connect = _disconnect = close = getresponse = dummy

    def read(self):
        response = self.__dict__

        if self.data_response_should_be_list:
            response = [self.__dict__]

        return json.dumps({"stat":"OK", "response":response},
                              cls=MockObjectJsonEncoder)

    def request(self, method, uri, body, headers):
        self.method = method
        self.uri = uri
        self.body = body

        self.headers = {}
        for k, v in headers.items():
            if isinstance(k, six.binary_type):
                k = k.decode('ascii')
            if isinstance(v, six.binary_type):
                v = v.decode('ascii')
            self.headers[k] = v

