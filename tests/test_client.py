import unittest
import urllib
import duo_client.client
import util


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
            **test
        )
        expected = 'f01811cbbf9561623ab45b893096267fd46a5178'
        expected = 'Basic ' + (ikey + ':' + expected).encode('base64').strip()
        self.assertEqual(actual,
                         expected)


class TestRequest(unittest.TestCase):
    """ Tests for the request created by api_call and json_api_call. """
    # usful args for testing
    args_in = {
        'foo':['bar'],
        'baz':['qux', 'quux=quuux', 'foobar=foobar&barbaz=barbaz']}
    args_out = dict(
        (key, [urllib.quote(v) for v in val])
        for (key, val) in args_in.items())

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


if __name__ == '__main__':
    unittest.main()

