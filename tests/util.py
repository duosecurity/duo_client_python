from __future__ import absolute_import
import json
import collections
import urllib

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
        param_dict[key].append(six.moves.urllib.parse.unquote(val))
    return param_dict


class MockHTTPConnection(object):
    """
    Mock HTTP(S) connection that returns a dummy JSON response.
    """
    status = 200            # success!

    def __init__(
        self,
        data_response_should_be_list=False,
        data_response_from_get_authlog=False,
        data_response_from_get_dtm_events=False,
        data_response_from_get_items=False,
    ):
        # if a response object should be a list rather than
        # a dict, then set this flag to true
        self.data_response_should_be_list = data_response_should_be_list
        self.data_response_from_get_authlog = data_response_from_get_authlog
        self.data_response_from_get_dtm_events = data_response_from_get_dtm_events
        self.data_response_from_get_items = data_response_from_get_items

    def dummy(self):
        return self

    _connect = _disconnect = close = getresponse = dummy

    def read(self):
        response = self.__dict__

        if self.data_response_should_be_list:
            response = [self.__dict__]

        if self.data_response_from_get_authlog:
            response['authlogs'] = []

        if self.data_response_from_get_items:
            response['items'] = []

        if self.data_response_from_get_dtm_events:
            response['events'] = [{"foo": "bar"}, {"bar": "foo"}]

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


class MockJsonObject(object):
    def to_json(self):
        return {'id': id(self)}

class CountingClient(duo_client.client.Client):
    def __init__(self, *args, **kwargs):
        super(CountingClient, self).__init__(*args, **kwargs)
        self.counter = 0

    def _make_request(self, *args, **kwargs):
        self.counter += 1
        return super(CountingClient, self)._make_request(*args, **kwargs)


class MockPagingHTTPConnection(MockHTTPConnection):
    def __init__(self, objects=None):
        if objects is not None:
            self.objects = objects

    def dummy(self):
        return self

    _connect = _disconnect = close = getresponse = dummy

    def read(self):
        metadata = {}
        metadata['total_objects'] = len(self.objects)
        if self.offset + self.limit < len(self.objects):
            metadata['next_offset'] = self.offset + self.limit
        if self.offset > 0:
            metadata['prev_offset'] = max(self.offset-self.limit, 0)

        return json.dumps(
                {"stat":"OK",
                "response": self.objects[self.offset: self.offset+self.limit],
                "metadata": metadata},
                cls=MockObjectJsonEncoder)

    def request(self, method, uri, body, headers):
        self.method = method
        self.uri = uri
        self.body = body
        self.headers = headers
        parsed = six.moves.urllib.parse.urlparse(uri)
        params = six.moves.urllib.parse.parse_qs(parsed.query)

        self.limit = int(params['limit'][0])
        self.offset = int(params['offset'][0])


class MockMultipleRequestHTTPConnection(MockHTTPConnection):
    def __init__(self, statuses):
        super(MockMultipleRequestHTTPConnection, self).__init__()
        self.statuses = statuses
        self.status_iterator = iter(statuses)
        self.requests = 0
        self.status = None

    def read(self):
        response = {'foo': 'bar'}
        return json.dumps({"stat":"OK", "response":response},
                              cls=MockObjectJsonEncoder)

    def request(self, method, uri, body, headers):
        self.requests += 1
        self.status = next(self.status_iterator)
        super(MockMultipleRequestHTTPConnection, self).request(
            method, uri, body, headers)
