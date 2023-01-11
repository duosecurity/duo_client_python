from __future__ import absolute_import
import hashlib
import mock
import unittest
import six.moves.urllib
import duo_client.client
from . import util
import base64
import collections
import json

JSON_BODY = {
            'data': 'abc123',
            'alpha': ['a', 'b', 'c', 'd'],
            'info': {
                'test': 1,
                'another': 2,
            }
        }
JSON_STRING = '{"alpha":["a","b","c","d"],"data":"abc123","info":{"another":2,"test":1}}'


class TestQueryParameters(unittest.TestCase):
    """
    Tests for the proper canonicalization of query parameters for signing.
    """
    def assert_canon_params(self, params, expected):
        params = duo_client.client.normalize_params(params)
        self.assertEqual(
            duo_client.client.canon_params(params),
            expected,
        )

    def test_zero_params(self):
        self.assert_canon_params(
            {},
            '',
        )

    def test_one_param(self):
        self.assert_canon_params(
            {'realname': ['First Last']},
            'realname=First%20Last',
        )

    def test_two_params(self):
        self.assert_canon_params(
            {'realname': ['First Last'], 'username': ['root']},
            'realname=First%20Last&username=root')

    def test_with_boolean_true_int_and_string(self):
        self.assert_canon_params(
            {'words': ['First Last'], 'success': [True], 'digit': [5]},
            'digit=5&success=true&words=First%20Last')

    def test_with_boolean_false_int_and_string(self):
        self.assert_canon_params(
            {'words': ['First Last'], 'success': [False], 'digit': [5]},
            'digit=5&success=false&words=First%20Last')

    def test_list_string(self):
        """ A list and a string will both get converted. """
        self.assert_canon_params(
            {'realname': 'First Last', 'username': ['root']},
            'realname=First%20Last&username=root')

    def test_printable_ascii_characters(self):
        self.assert_canon_params(
            {
                'digits': ['0123456789'],
                'letters': ['abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'],
                'punctuation': ['!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'],
                'whitespace': ['\t\n\x0b\x0c\r '],
            },
            'digits=0123456789&letters=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ&punctuation=%21%22%23%24%25%26%27%28%29%2A%2B%2C-.%2F%3A%3B%3C%3D%3E%3F%40%5B%5C%5D%5E_%60%7B%7C%7D~&whitespace=%09%0A%0B%0C%0D%20'
        )

    def test_unicode_fuzz_values(self):
        self.assert_canon_params(
            {
                u'bar': [u'\u2815\uaaa3\u37cf\u4bb7\u36e9\ucc05\u668e\u8162\uc2bd\ua1f1'],
                u'baz': [u'\u0df3\u84bd\u5669\u9985\ub8a4\uac3a\u7be7\u6f69\u934a\ub91c'],
                u'foo': [u'\ud4ce\ud6d6\u7938\u50c0\u8a20\u8f15\ufd0b\u8024\u5cb3\uc655'],
                u'qux': [u'\u8b97\uc846-\u828e\u831a\uccca\ua2d4\u8c3e\ub8b2\u99be'],
            },
            'bar=%E2%A0%95%EA%AA%A3%E3%9F%8F%E4%AE%B7%E3%9B%A9%EC%B0%85%E6%9A%8E%E8%85%A2%EC%8A%BD%EA%87%B1&baz=%E0%B7%B3%E8%92%BD%E5%99%A9%E9%A6%85%EB%A2%A4%EA%B0%BA%E7%AF%A7%E6%BD%A9%E9%8D%8A%EB%A4%9C&foo=%ED%93%8E%ED%9B%96%E7%A4%B8%E5%83%80%E8%A8%A0%E8%BC%95%EF%B4%8B%E8%80%A4%E5%B2%B3%EC%99%95&qux=%E8%AE%97%EC%A1%86-%E8%8A%8E%E8%8C%9A%EC%B3%8A%EA%8B%94%E8%B0%BE%EB%A2%B2%E9%A6%BE',
        )

    def test_unicode_fuzz_keys_and_values(self):
        self.assert_canon_params(
            {
                u'\u469a\u287b\u35d0\u8ef3\u6727\u502a\u0810\ud091\xc8\uc170': [u'\u0f45\u1a76\u341a\u654c\uc23f\u9b09\uabe2\u8343\u1b27\u60d0'],
                u'\u7449\u7e4b\uccfb\u59ff\ufe5f\u83b7\uadcc\u900c\ucfd1\u7813': [u'\u8db7\u5022\u92d3\u42ef\u207d\u8730\uacfe\u5617\u0946\u4e30'],
                u'\u7470\u9314\u901c\u9eae\u40d8\u4201\u82d8\u8c70\u1d31\ua042': [u'\u17d9\u0ba8\u9358\uaadf\ua42a\u48be\ufb96\u6fe9\ub7ff\u32f3'],
                u'\uc2c5\u2c1d\u2620\u3617\u96b3F\u8605\u20e8\uac21\u5934': [u'\ufba9\u41aa\ubd83\u840b\u2615\u3e6e\u652d\ua8b5\ud56bU'],
            },
            '%E4%9A%9A%E2%A1%BB%E3%97%90%E8%BB%B3%E6%9C%A7%E5%80%AA%E0%A0%90%ED%82%91%C3%88%EC%85%B0=%E0%BD%85%E1%A9%B6%E3%90%9A%E6%95%8C%EC%88%BF%E9%AC%89%EA%AF%A2%E8%8D%83%E1%AC%A7%E6%83%90&%E7%91%89%E7%B9%8B%EC%B3%BB%E5%A7%BF%EF%B9%9F%E8%8E%B7%EA%B7%8C%E9%80%8C%EC%BF%91%E7%A0%93=%E8%B6%B7%E5%80%A2%E9%8B%93%E4%8B%AF%E2%81%BD%E8%9C%B0%EA%B3%BE%E5%98%97%E0%A5%86%E4%B8%B0&%E7%91%B0%E9%8C%94%E9%80%9C%E9%BA%AE%E4%83%98%E4%88%81%E8%8B%98%E8%B1%B0%E1%B4%B1%EA%81%82=%E1%9F%99%E0%AE%A8%E9%8D%98%EA%AB%9F%EA%90%AA%E4%A2%BE%EF%AE%96%E6%BF%A9%EB%9F%BF%E3%8B%B3&%EC%8B%85%E2%B0%9D%E2%98%A0%E3%98%97%E9%9A%B3F%E8%98%85%E2%83%A8%EA%B0%A1%E5%A4%B4=%EF%AE%A9%E4%86%AA%EB%B6%83%E8%90%8B%E2%98%95%E3%B9%AE%E6%94%AD%EA%A2%B5%ED%95%ABU',
        )

    def test_sort_order_with_common_prefix(self):
        self.assert_canon_params(
            {
                'foo_bar': '2',
                'foo': '1',
            },
            'foo=1&foo_bar=2',
        )


class TestCanonicalize(unittest.TestCase):
    """
    Tests of the canonicalization of request attributes and parameters
    for signing.
    """
    def test_v1(self):
        test = {
            'host': 'foO.BAr52.cOm',
            'method': 'PoSt',
            'params': {
                u'\u469a\u287b\u35d0\u8ef3\u6727\u502a\u0810\ud091\xc8\uc170': [u'\u0f45\u1a76\u341a\u654c\uc23f\u9b09\uabe2\u8343\u1b27\u60d0'],
                u'\u7449\u7e4b\uccfb\u59ff\ufe5f\u83b7\uadcc\u900c\ucfd1\u7813': [u'\u8db7\u5022\u92d3\u42ef\u207d\u8730\uacfe\u5617\u0946\u4e30'],
                u'\u7470\u9314\u901c\u9eae\u40d8\u4201\u82d8\u8c70\u1d31\ua042': [u'\u17d9\u0ba8\u9358\uaadf\ua42a\u48be\ufb96\u6fe9\ub7ff\u32f3'],
                u'\uc2c5\u2c1d\u2620\u3617\u96b3F\u8605\u20e8\uac21\u5934': [u'\ufba9\u41aa\ubd83\u840b\u2615\u3e6e\u652d\ua8b5\ud56bU'],
            },
            'uri': '/Foo/BaR2/qux',
        }
        test['params'] = duo_client.client.normalize_params(test['params'])
        self.assertEqual(duo_client.client.canonicalize(sig_version=1,
                                                        date=None,
                                                        **test),
                         'POST\nfoo.bar52.com\n/Foo/BaR2/qux\n%E4%9A%9A%E2%A1%BB%E3%97%90%E8%BB%B3%E6%9C%A7%E5%80%AA%E0%A0%90%ED%82%91%C3%88%EC%85%B0=%E0%BD%85%E1%A9%B6%E3%90%9A%E6%95%8C%EC%88%BF%E9%AC%89%EA%AF%A2%E8%8D%83%E1%AC%A7%E6%83%90&%E7%91%89%E7%B9%8B%EC%B3%BB%E5%A7%BF%EF%B9%9F%E8%8E%B7%EA%B7%8C%E9%80%8C%EC%BF%91%E7%A0%93=%E8%B6%B7%E5%80%A2%E9%8B%93%E4%8B%AF%E2%81%BD%E8%9C%B0%EA%B3%BE%E5%98%97%E0%A5%86%E4%B8%B0&%E7%91%B0%E9%8C%94%E9%80%9C%E9%BA%AE%E4%83%98%E4%88%81%E8%8B%98%E8%B1%B0%E1%B4%B1%EA%81%82=%E1%9F%99%E0%AE%A8%E9%8D%98%EA%AB%9F%EA%90%AA%E4%A2%BE%EF%AE%96%E6%BF%A9%EB%9F%BF%E3%8B%B3&%EC%8B%85%E2%B0%9D%E2%98%A0%E3%98%97%E9%9A%B3F%E8%98%85%E2%83%A8%EA%B0%A1%E5%A4%B4=%EF%AE%A9%E4%86%AA%EB%B6%83%E8%90%8B%E2%98%95%E3%B9%AE%E6%94%AD%EA%A2%B5%ED%95%ABU')

    def test_v2(self):
        test = {
            'date': 'Fri, 07 Dec 2012 17:18:00 -0000',
            'host': 'foO.BAr52.cOm',
            'method': 'PoSt',
            'params': {u'\u469a\u287b\u35d0\u8ef3\u6727\u502a\u0810\ud091\xc8\uc170': [u'\u0f45\u1a76\u341a\u654c\uc23f\u9b09\uabe2\u8343\u1b27\u60d0'],
                       u'\u7449\u7e4b\uccfb\u59ff\ufe5f\u83b7\uadcc\u900c\ucfd1\u7813': [u'\u8db7\u5022\u92d3\u42ef\u207d\u8730\uacfe\u5617\u0946\u4e30'],
                       u'\u7470\u9314\u901c\u9eae\u40d8\u4201\u82d8\u8c70\u1d31\ua042': [u'\u17d9\u0ba8\u9358\uaadf\ua42a\u48be\ufb96\u6fe9\ub7ff\u32f3'],
                       u'\uc2c5\u2c1d\u2620\u3617\u96b3F\u8605\u20e8\uac21\u5934': [u'\ufba9\u41aa\ubd83\u840b\u2615\u3e6e\u652d\ua8b5\ud56bU']},
            'uri': '/Foo/BaR2/qux',
        }
        test['params'] = duo_client.client.normalize_params(test['params'])
        self.assertEqual(duo_client.client.canonicalize(sig_version=2,
                                                        **test),
                         'Fri, 07 Dec 2012 17:18:00 -0000\nPOST\nfoo.bar52.com\n/Foo/BaR2/qux\n%E4%9A%9A%E2%A1%BB%E3%97%90%E8%BB%B3%E6%9C%A7%E5%80%AA%E0%A0%90%ED%82%91%C3%88%EC%85%B0=%E0%BD%85%E1%A9%B6%E3%90%9A%E6%95%8C%EC%88%BF%E9%AC%89%EA%AF%A2%E8%8D%83%E1%AC%A7%E6%83%90&%E7%91%89%E7%B9%8B%EC%B3%BB%E5%A7%BF%EF%B9%9F%E8%8E%B7%EA%B7%8C%E9%80%8C%EC%BF%91%E7%A0%93=%E8%B6%B7%E5%80%A2%E9%8B%93%E4%8B%AF%E2%81%BD%E8%9C%B0%EA%B3%BE%E5%98%97%E0%A5%86%E4%B8%B0&%E7%91%B0%E9%8C%94%E9%80%9C%E9%BA%AE%E4%83%98%E4%88%81%E8%8B%98%E8%B1%B0%E1%B4%B1%EA%81%82=%E1%9F%99%E0%AE%A8%E9%8D%98%EA%AB%9F%EA%90%AA%E4%A2%BE%EF%AE%96%E6%BF%A9%EB%9F%BF%E3%8B%B3&%EC%8B%85%E2%B0%9D%E2%98%A0%E3%98%97%E9%9A%B3F%E8%98%85%E2%83%A8%EA%B0%A1%E5%A4%B4=%EF%AE%A9%E4%86%AA%EB%B6%83%E8%90%8B%E2%98%95%E3%B9%AE%E6%94%AD%EA%A2%B5%ED%95%ABU')

    def test_v4_with_json(self):
        hashed_body = hashlib.sha512(JSON_STRING.encode('utf-8')).hexdigest()
        expected = (
            'Tue, 04 Jul 2017 14:12:00\n'
            'POST\n'
            'foo.bar52.com\n'
            '/Foo/BaR2/qux\n\n' + hashed_body)
        params = {}
        actual = duo_client.client.canonicalize(
            'POST', 'foO.BaR52.cOm', '/Foo/BaR2/qux', params,
            'Tue, 04 Jul 2017 14:12:00', sig_version=4, body=JSON_STRING)

        self.assertEqual(actual, expected)

    def test_v5_with_json(self):
        hashed_body = hashlib.sha512(JSON_STRING.encode('utf-8')).hexdigest()
        headers = {"X-Duo-Header-1": "header_value_1"}
        expected = (
                'Tue, 17 Nov 2020 14:12:00\n'
                'POST\n'
                'foo.bar52.com\n'
                '/Foo/BaR2/qux\n\n' + hashed_body
                +'\n630b4bfe7e9abd03da2eee8f0a5d4e60a254ec880a839bcc2223bb5b9443e8ef24d58f0'
                 '254f1f5934bf8c017ebd0fd5b1acf86766bdbe74185e712a4092df3ed')
        params = {}
        body = duo_client.client.Client.canon_json(JSON_BODY)
        actual = duo_client.client.canonicalize(
            'POST', 'foO.BaR52.cOm', '/Foo/BaR2/qux', params, 'Tue, 17 Nov 2020 14:12:00',
            sig_version=5, body=body, additional_headers=headers)

    def test_invalid_signature_version_raises(self):
        params = duo_client.client.Client.canon_json(JSON_BODY)
        with self.assertRaises(ValueError) as e:
            duo_client.client.canonicalize(
                'POST', 'foO.BaR52.cOm', '/Foo/BaR2/qux', params,
                'Tue, 04 Jul 2017 14:12:00', sig_version=999)
        self.assertEqual(
            e.exception.args[0],
            "Unknown signature version: {}".format(999))


class TestNormalizePageArgs(unittest.TestCase):

    def setUp(self):
        self.client = duo_client.client.Client(
            'test_ikey', 'test_akey', 'example.com')

    def test_normalize_page_args(self):

        tests = [
            (
                {},
                (None, '0')
            ),
            (
                {'offset': 9001},
                (None, '9001'),
            ),
            (
                {'limit': 2},
                ('2', '0'),
            ),
            (
                {'limit': '3'},
                ('3', '0'),
            ),
            (
                {'limit': 5, 'offset': 9002},
                ('5', '9002')
            )
        ]

        for (input, expected) in tests:
            output = self.client.normalize_paging_args(**input)
            self.assertEqual(output, expected)


class TestSign(unittest.TestCase):
    """
    Tests for proper signature creation for a request.
    """
    def test_hmac_sha1(self):
        test = {
            'date': 'Fri, 07 Dec 2012 17:18:00 -0000',
            'host': 'foO.BAr52.cOm',
            'method': 'PoSt',
            'params': {u'\u469a\u287b\u35d0\u8ef3\u6727\u502a\u0810\ud091\xc8\uc170': [u'\u0f45\u1a76\u341a\u654c\uc23f\u9b09\uabe2\u8343\u1b27\u60d0'],
                       u'\u7449\u7e4b\uccfb\u59ff\ufe5f\u83b7\uadcc\u900c\ucfd1\u7813': [u'\u8db7\u5022\u92d3\u42ef\u207d\u8730\uacfe\u5617\u0946\u4e30'],
                       u'\u7470\u9314\u901c\u9eae\u40d8\u4201\u82d8\u8c70\u1d31\ua042': [u'\u17d9\u0ba8\u9358\uaadf\ua42a\u48be\ufb96\u6fe9\ub7ff\u32f3'],
                       u'\uc2c5\u2c1d\u2620\u3617\u96b3F\u8605\u20e8\uac21\u5934': [u'\ufba9\u41aa\ubd83\u840b\u2615\u3e6e\u652d\ua8b5\ud56bU']},
            'uri': '/Foo/BaR2/qux',
        }
        test['params'] = duo_client.client.normalize_params(test['params'])
        ikey = 'test_ikey'
        actual = duo_client.client.sign(
            sig_version=2,
            ikey=ikey,
            skey='gtdfxv9YgVBYcF6dl2Eq17KUQJN2PLM2ODVTkvoT',
            digestmod=hashlib.sha1,
            **test
        )
        expected = 'f01811cbbf9561623ab45b893096267fd46a5178'
        expected = ikey + ':' + expected
        if isinstance(expected, six.text_type):
            expected = expected.encode('utf-8')
        expected = base64.b64encode(expected).strip()
        if not isinstance(expected, six.text_type):
            expected = expected.decode('utf-8')
        expected = 'Basic ' + expected
        self.assertEqual(actual,
                         expected)

    def test_hmac_sha512(self):
        test = {
            'date': 'Fri, 07 Dec 2012 17:18:00 -0000',
            'host': 'foO.BAr52.cOm',
            'method': 'PoSt',
            'params': {u'\u469a\u287b\u35d0\u8ef3\u6727\u502a\u0810\ud091\xc8\uc170': [u'\u0f45\u1a76\u341a\u654c\uc23f\u9b09\uabe2\u8343\u1b27\u60d0'],
                       u'\u7449\u7e4b\uccfb\u59ff\ufe5f\u83b7\uadcc\u900c\ucfd1\u7813': [u'\u8db7\u5022\u92d3\u42ef\u207d\u8730\uacfe\u5617\u0946\u4e30'],
                       u'\u7470\u9314\u901c\u9eae\u40d8\u4201\u82d8\u8c70\u1d31\ua042': [u'\u17d9\u0ba8\u9358\uaadf\ua42a\u48be\ufb96\u6fe9\ub7ff\u32f3'],
                       u'\uc2c5\u2c1d\u2620\u3617\u96b3F\u8605\u20e8\uac21\u5934': [u'\ufba9\u41aa\ubd83\u840b\u2615\u3e6e\u652d\ua8b5\ud56bU']},
            'uri': '/Foo/BaR2/qux',
        }
        test['params'] = duo_client.client.normalize_params(test['params'])
        ikey = 'test_ikey'
        actual = duo_client.client.sign(
            sig_version=2,
            ikey=ikey,
            skey='gtdfxv9YgVBYcF6dl2Eq17KUQJN2PLM2ODVTkvoT',
            **test
        )
        expected = '0508065035a03b2a1de2f453e629e791d180329e157f65df6b3e0f08299d4321e1c5c7a7c7ee6b9e5fc80d1fb6fbf3ad5eb7c44dd3b3985a02c37aca53ec3698'
        expected = ikey + ':' + expected
        if isinstance(expected, six.text_type):
            expected = expected.encode('utf-8')
        expected = base64.b64encode(expected).strip()
        if not isinstance(expected, six.text_type):
            expected = expected.decode('utf-8')
        expected = 'Basic ' + expected
        self.assertEqual(actual,
                         expected)
                         
class TestRequest(unittest.TestCase):
    """ Tests for the request created by api_call and json_api_call. """
    # usful args for testing
    args_in = {
        'foo':['bar'],
        'baz':['qux', 'quux=quuux', 'foobar=foobar&barbaz=barbaz']}
    args_out = dict(
        (key, [v for v in val])
        for (key, val) in list(args_in.items()))

    def setUp(self):
        self.client = duo_client.client.Client(
            'test_ikey', 'test_akey', 'example.com')
        # monkeypatch client's _connect()
        self.client._connect = lambda: util.MockHTTPConnection()

    def test_api_call_get_no_params(self):
        (response, dummy) = self.client.api_call('GET', '/foo/bar', {})
        self.assertEqual(response.method, 'GET')
        self.assertEqual(response.uri, '/foo/bar?')

    def test_api_call_post_no_params(self):
        (response, dummy) = self.client.api_call('POST', '/foo/bar', {})
        self.assertEqual(response.method, 'POST')
        self.assertEqual(response.uri, '/foo/bar')
        self.assertEqual(response.body, '')

    def test_api_call_get_params(self):
        (response, dummy) = self.client.api_call(
            'GET', '/foo/bar', self.args_in)
        self.assertEqual(response.method, 'GET')
        (uri, args) = response.uri.split('?')
        self.assertEqual(uri, '/foo/bar')
        self.assertEqual(util.params_to_dict(args), self.args_out)

    def test_api_call_post_params(self):
        (response, dummy) = self.client.api_call(
            'POST', '/foo/bar', self.args_in)
        self.assertEqual(response.method, 'POST')
        self.assertEqual(response.uri, '/foo/bar')
        self.assertEqual(util.params_to_dict(response.body), self.args_out)

    def test_json_api_call_get_no_params(self):
        response = self.client.json_api_call('GET', '/foo/bar', {})
        self.assertEqual(response['method'], 'GET')
        self.assertEqual(response['uri'], '/foo/bar?')
        self.assertEqual(response['body'], None)

    def test_json_api_call_post_no_params(self):
        response = self.client.json_api_call('POST', '/foo/bar', {})
        self.assertEqual(response['method'], 'POST')
        self.assertEqual(response['uri'], '/foo/bar')
        self.assertEqual(response['body'], '')

    def test_json_api_call_get_params(self):
        response = self.client.json_api_call(
            'GET', '/foo/bar', self.args_in)
        self.assertEqual(response['method'], 'GET')
        (uri, args) = response['uri'].split('?')
        self.assertEqual(uri, '/foo/bar')
        self.assertEqual(util.params_to_dict(args), self.args_out)

    def test_json_api_call_post_params(self):
        response = self.client.json_api_call(
            'POST', '/foo/bar', self.args_in)
        self.assertEqual(response['method'], 'POST')
        self.assertEqual(response['uri'], '/foo/bar')
        self.assertEqual(util.params_to_dict(response['body']), self.args_out)

class TestPaging(unittest.TestCase):
    def setUp(self):
        self.client = util.CountingClient(
            'test_ikey', 'test_akey', 'example.com', paging_limit=100)
        self.objects = [util.MockJsonObject() for i in range(1000)]
        self.client._connect = lambda: util.MockPagingHTTPConnection(self.objects)

    def test_get_objects_paging(self):
        response = self.client.json_paging_api_call(
            'GET', '/admin/v1/objects', {})
        self.assertEqual(len(self.objects), len(list(response)))
        self.assertEqual(10, self.client.counter)

    def test_get_no_objects_paging(self):
        self.objects = []
        self.client._connect = lambda: util.MockPagingHTTPConnection(self.objects)
        response = self.client.json_paging_api_call(
            'GET', '/admin/v1/objects', {})
        self.assertEqual(len(self.objects), len(list(response)))
        self.assertEqual(1, self.client.counter)

    def test_get_objects_paging_limit(self):
        response = self.client.json_paging_api_call(
            'GET', '/admin/v1/objects', {'limit':'250'})
        self.assertEqual(len(self.objects), len(list(response)))
        self.assertEqual(4, self.client.counter)

    def test_get_all_objects(self):
        response = self.client.json_paging_api_call(
            'GET', '/admin/v1/objects', {'limit':'1000'})
        expected = [obj.to_json() for obj in self.objects]
        self.assertListEqual(expected, list(response))
        self.assertEqual(1, self.client.counter)

class TestRequestsV4(unittest.TestCase):
    # usful args for testing GETs
    args_in = {
        'foo':['bar'],
        'baz':['qux', 'quux=quuux', 'foobar=foobar&barbaz=barbaz']}
    args_out = dict(
        (key, [v for v in val])
        for (key, val) in list(args_in.items()))

    def setUp(self):
        self.client = duo_client.client.Client(
            'test_ikey', 'test_akey', 'example.com', sig_timezone='America/Detroit',
            digestmod=hashlib.sha512, sig_version=4)
        # monkeypatch client's _connect()
        self.client._connect = lambda: util.MockHTTPConnection()

    def test_get_no_params(self):
        (response, dummy) = self.client.api_call('GET', '/foo/bar', {})
        self.assertEqual(response.method, 'GET')
        self.assertEqual(response.uri, '/foo/bar?')
        self.assertIn('Authorization', response.headers)

    def test_get_params(self):
        (response, dummy) = self.client.api_call(
            'GET', '/foo/bar', self.args_in)
        self.assertEqual(response.method, 'GET')
        (uri, args) = response.uri.split('?')
        self.assertEqual(uri, '/foo/bar')
        self.assertEqual(util.params_to_dict(args), self.args_out)
        self.assertIn('Authorization', response.headers)

    def test_json_api_call_get_no_params(self):
        response = self.client.json_api_call('GET', '/foo/bar', {})
        self.assertEqual(response['method'], 'GET')
        self.assertEqual(response['uri'], '/foo/bar?')
        self.assertEqual(response['body'], None)
        self.assertIn('Authorization', response['headers'])

    def test_json_api_call_get_params(self):
        response = self.client.json_api_call(
            'GET', '/foo/bar', self.args_in)
        self.assertEqual(response['method'], 'GET')
        (uri, args) = response['uri'].split('?')
        self.assertEqual(uri, '/foo/bar')
        self.assertEqual(util.params_to_dict(args), self.args_out)
        self.assertIn('Authorization', response['headers'])

    def test_json_post(self):
        (response, dummy) = self.client.api_call('POST', '/foo/bar', JSON_BODY)

        self.assertEqual(response.method, 'POST')
        self.assertEqual(response.uri, '/foo/bar')
        self.assertEqual(response.body, JSON_STRING)

        self.assertIn('Content-type', response.headers)
        self.assertEqual(response.headers['Content-type'], 'application/json')
        self.assertIn('Authorization', response.headers)

    def test_json_fails_with_bad_args(self):
        with self.assertRaises(ValueError) as e:
            (response, dummy) = self.client.api_call('POST', '/foo/bar', '')
        self.assertEqual(e.exception.args[0], "JSON request must be an object.")

    def test_json_put(self):
        (response, dummy) = self.client.api_call('PUT', '/foo/bar', JSON_BODY)

        self.assertEqual(response.method, 'PUT')
        self.assertEqual(response.uri, '/foo/bar')
        self.assertEqual(response.body, JSON_STRING)

        self.assertIn('Content-type', response.headers)
        self.assertEqual(response.headers['Content-type'], 'application/json')
        self.assertIn('Authorization', response.headers)

class TestParseJsonResponse(unittest.TestCase):
    APIResponse = collections.namedtuple('APIResponse', 'status reason')

    def setUp(self):
        self.client = duo_client.client.Client(
            'test_ikey', 'test_akey', 'example.com', sig_timezone='America/Detroit',
            sig_version=2)

    def test_good_response(self):
        api_res = self.APIResponse(200, '')
        expected_data = {
            'foo': 'bar'
        }
        res_body = {
            'response': expected_data,
            'stat': 'OK'
        }

        data = self.client.parse_json_response(api_res, json.dumps(res_body))

        self.assertEqual(data, expected_data)

    def test_response_contains_invalid_json(self):
        api_res = self.APIResponse(200, 'Fake reason')

        response = 'Bad JSON'
        with self.assertRaises(RuntimeError) as e:
            self.client.parse_json_response(api_res, response)

        self.assertEqual(e.exception.status, api_res.status)
        self.assertEqual(e.exception.reason, api_res.reason)
        self.assertEqual(e.exception.data, response)

    def test_response_stat_isnot_OK(self):
        api_res = self.APIResponse(200, 'Fake reason')

        res_body = {
                'response': {
                'foo': 'bar'
            },
            'stat': 'FAIL'
        }

        with self.assertRaises(RuntimeError) as e:
            self.client.parse_json_response(api_res, json.dumps(res_body))

        self.assertEqual(e.exception.status, api_res.status)
        self.assertEqual(e.exception.reason, api_res.reason)
        self.assertEqual(e.exception.data, res_body)

    def test_response_is_http_error(self):
        for code in range(201, 600):
            api_res = self.APIResponse(code, 'fake reason')
            res_body = {
                'response': 'some message',
                'stat': 'OK'
            }
            with self.assertRaises(RuntimeError) as e:
                self.client.parse_json_response(api_res, json.dumps(res_body))

            self.assertEqual(e.exception.status, api_res.status)
            self.assertEqual(e.exception.reason, api_res.reason)
            self.assertEqual(e.exception.data, res_body)

class TestParseJsonResponseAndMetadata(unittest.TestCase):
    APIResponse = collections.namedtuple('APIResponse', 'status reason')

    def setUp(self):
        self.client = duo_client.client.Client(
            'test_ikey', 'test_akey', 'example.com', sig_timezone='America/Detroit',
            sig_version=2)

    def test_good_response(self):
        api_res = self.APIResponse(200, '')
        expected_data = {
            'foo': 'bar'
        }
        res_body = {
            'response': expected_data,
            'stat': 'OK'
        }

        data, metadata = self.client.parse_json_response_and_metadata(api_res, json.dumps(res_body))

        self.assertEqual(data, expected_data)
        self.assertEqual(metadata, {})

    def test_response_contains_invalid_json(self):
        api_res = self.APIResponse(200, 'Fake reason')

        response = 'Bad JSON'
        with self.assertRaises(RuntimeError) as e:
            self.client.parse_json_response_and_metadata(api_res, response)

        self.assertEqual(e.exception.status, api_res.status)
        self.assertEqual(e.exception.reason, api_res.reason)
        self.assertEqual(e.exception.data, response)

    def test_response_stat_isnot_OK(self):
        api_res = self.APIResponse(200, 'Fake reason')

        res_body = {
                'response': {
                'foo': 'bar'
            },
            'stat': 'FAIL'
        }

        with self.assertRaises(RuntimeError) as e:
            self.client.parse_json_response_and_metadata(api_res, json.dumps(res_body))

        self.assertEqual(e.exception.status, api_res.status)
        self.assertEqual(e.exception.reason, api_res.reason)
        self.assertEqual(e.exception.data, res_body)

    def test_response_is_http_error(self):
        for code in range(201, 600):
            api_res = self.APIResponse(code, 'fake reason')
            res_body = {
                'response': 'some message',
                'stat': 'OK'
            }
            with self.assertRaises(RuntimeError) as e:
                self.client.parse_json_response_and_metadata(api_res, json.dumps(res_body))

            self.assertEqual(e.exception.status, api_res.status)
            self.assertEqual(e.exception.reason, api_res.reason)
            self.assertEqual(e.exception.data, res_body)

@mock.patch('duo_client.client.sleep')
class TestRetryRequests(unittest.TestCase):
    def setUp(self):
        self.client = duo_client.client.Client(
            'test_ikey', 'test_akey', 'example.com',
        )

    def test_non_limited_reponse(self, mock_sleep):
        # monkeypatch client's _connect()
        mock_connection = util.MockMultipleRequestHTTPConnection(
            [200])
        self.client._connect = lambda: mock_connection
        (response, dummy) = self.client.api_call('GET', '/foo/bar', {})
        mock_sleep.assert_not_called()

        self.assertEqual(response.status, 200)
        self.assertEqual(mock_connection.requests, 1)

    @mock.patch('duo_client.client.random')
    def test_single_limited_response(self, mock_random, mock_sleep):
        mock_random.uniform.return_value = 0.123
        # monkeypatch client's _connect()
        mock_connection = util.MockMultipleRequestHTTPConnection(
            [429, 200])
        self.client._connect = lambda: mock_connection

        (response, dummy) = self.client.api_call('GET', '/foo/bar', {})

        mock_sleep.assert_called_once_with(1.123)
        mock_random.uniform.assert_called_once()
        self.assertEqual(response.status, 200)
        self.assertEqual(mock_connection.requests, 2)

    @mock.patch('duo_client.client.random')
    def test_all_limited_responses(self, mock_random, mock_sleep):
        mock_random.uniform.return_value = 0.123
        # monkeypatch client's _connect()
        mock_connection = util.MockMultipleRequestHTTPConnection(
            [429, 429, 429, 429, 429, 429, 429])
        self.client._connect = lambda: mock_connection

        (response, data) = self.client.api_call('GET', '/foo/bar', {})

        expected_sleep_calls = (
            mock.call(1.123),
            mock.call(2.123),
            mock.call(4.123),
            mock.call(8.123),
            mock.call(16.123),
            mock.call(32.123),
        )
        mock_sleep.assert_has_calls(expected_sleep_calls)
        expected_random_calls = (
            mock.call(0, 1),
            mock.call(0, 1),
            mock.call(0, 1),
            mock.call(0, 1),
            mock.call(0, 1),
            mock.call(0, 1),
        )
        mock_random.uniform.assert_has_calls(expected_random_calls)
        self.assertEqual(response.status, 429)
        self.assertEqual(mock_connection.requests, 7)

class TestInstantiate(unittest.TestCase):
    def test_sig_version_3_raises_exception(self):
        with self.assertRaises(ValueError):
            duo_client.client.Client(
                'test_ikey', 'test_akey', 'example.com', sig_timezone='America/Detroit',
                sig_version=3)

if __name__ == '__main__':
    unittest.main()
