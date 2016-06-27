from __future__ import absolute_import
import unittest
from . import util
import duo_client.admin


class TestAdmin(unittest.TestCase):

    def setUp(self):
        self.client = duo_client.admin.Admin(
            'test_ikey', 'test_akey', 'example.com')
        self.client.account_id = 'DA012345678901234567'
        # monkeypatch client's _connect()
        self.client._connect = lambda: util.MockHTTPConnection()

    # GET with no params
    def test_get_users(self):
        response = self.client.get_users()
        self.assertEqual(response['method'], 'GET')
        self.assertEqual(
            response['uri'],
            '/admin/v1/users?account_id=%s' % self.client.account_id)
        self.assertEqual(response['body'], None)

    # GET with params
    def test_get_users_by_name(self):
        response = self.client.get_users_by_name('foo')
        (uri, args) = response['uri'].split('?')
        self.assertEqual(response['method'], 'GET')
        self.assertEqual(uri, '/admin/v1/users')
        self.assertEqual(
            util.params_to_dict(args),
            {'username':['foo'],
             'account_id':[self.client.account_id]})
        self.assertEqual(response['body'], None)
        response = self.client.get_users_by_name('foo')
        (uri, args) = response['uri'].split('?')
        self.assertEqual(response['method'], 'GET')
        self.assertEqual(uri, '/admin/v1/users')
        self.assertEqual(
            util.params_to_dict(args),
            {'username':['foo'],
             'account_id':[self.client.account_id]})
        self.assertEqual(response['body'], None)

    # POST with params
    def test_add_user(self):
        # all params given
        response = self.client.add_user('foo', 'bar', 'active', 'notes')
        self.assertEqual(response['method'], 'POST')
        self.assertEqual(response['uri'], '/admin/v1/users')
        self.assertEqual(
            util.params_to_dict(response['body']),
            {'realname':['bar'],
             'notes':['notes'],
             'username':['foo'],
             'status':['active'],
             'account_id':[self.client.account_id]})
        # defaults
        response = self.client.add_user('bar')
        self.assertEqual(response['method'], 'POST')
        self.assertEqual(response['uri'], '/admin/v1/users')
        self.assertEqual(
            util.params_to_dict(response['body']),
            {'username':['bar'], 'account_id':[self.client.account_id]})

    # POST with no params
    def test_update_user(self):
        response = self.client.update_user('DU012345678901234567')
        self.assertEqual(response['method'], 'POST')
        self.assertEqual(
            response['uri'], '/admin/v1/users/DU012345678901234567')
        self.assertEqual(
            util.params_to_dict(response['body']),
            {'account_id':[self.client.account_id]})

    def test_get_endpoints(self):
        response = self.client.get_endpoints()
        self.assertEqual(response['method'], 'GET')
        (uri, args) = response['uri'].split('?')
        self.assertEqual(uri, '/admin/v1/endpoints')
        self.assertEqual(
            util.params_to_dict(args),
            {'account_id': [self.client.account_id]})

if __name__ == '__main__':
    unittest.main()

