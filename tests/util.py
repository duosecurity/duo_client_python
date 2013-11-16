import json
import collections

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

    def dummy(self):
        return self

    _connect = _disconnect = close = getresponse = dummy

    def read(self):
        return json.dumps({"stat":"OK", "response":self.__dict__})

    def request(self, method, uri, body, headers):
        self.method = method
        self.uri = uri
        self.body = body
        self.headers = headers
