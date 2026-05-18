import unittest
from .base import TestAuthorization
from .. import util


class TestPing(TestAuthorization):

    def test_ping(self):
        response = self.client.ping()
        self.assertEqual(response['method'], 'GET')
        self.assertIn('/authorize/v1/ping', response['uri'])


class TestCheck(TestAuthorization):

    def test_check(self):
        response = self.client.check()
        self.assertEqual(response['method'], 'GET')
        self.assertIn('/authorize/v1/check', response['uri'])


class TestEvaluate(TestAuthorization):

    def setUp(self):
        super().setUp()
        self.mock_conn = util.MockHTTPConnection()
        self.client._connect = lambda: self.mock_conn

    def test_evaluate(self):
        response = self.client.evaluate(
            access_token='test_token',
            mcp_server_id='server_123',
        )
        self.assertEqual(self.mock_conn.method, 'POST')
        self.assertIn('/authorize/v1/mcp_capabilities/evaluate', self.mock_conn.uri)
        self.assertIn('allowed_capabilities', response)
        self.assertIn('authorized', response)
        self.assertIn('expires_at', response)
        self.assertIn('user_id', response)
        self.assertIn('non_human_identity', response)
        self.assertIn('policy_version_id', response)

    def test_evaluate_with_optional_params(self):
        response = self.client.evaluate(
            access_token='test_token',
            mcp_server_id='server_123',
            mcp_server_name='my_server',
            tool='my_tool',
        )
        self.assertEqual(self.mock_conn.method, 'POST')
        self.assertIn('/authorize/v1/mcp_capabilities/evaluate', self.mock_conn.uri)


if __name__ == '__main__':
    unittest.main()
