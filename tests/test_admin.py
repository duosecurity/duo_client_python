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

        # if you are wanting to simulate getting lists of objects
        # rather than a single object
        self.client_list = duo_client.admin.Admin(
            'test_ikey', 'test_akey', 'example.com')
        self.client_list.account_id = 'DA012345678901234567'
        self.client_list._connect = \
            lambda: util.MockHTTPConnection(data_response_should_be_list=True)

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

    def test_get_user_u2ftokens(self):
        """ Test to get u2ftokens by user id.
        """
        response = self.client.get_user_u2ftokens('DU012345678901234567')
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'GET')
        self.assertEqual(uri, '/admin/v1/users/DU012345678901234567/u2ftokens')
        self.assertEqual(util.params_to_dict(args),
                         {'account_id':[self.client.account_id]})

    def test_get_u2ftokens_with_params(self):
        """ Test to get u2ftokens with params.
        """
        response = list(self.client_list.get_u2ftokens())[0]
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'GET')
        self.assertEqual(uri, '/admin/v1/u2ftokens')
        self.assertEqual(util.params_to_dict(args),
                         {'account_id':[self.client_list.account_id]})

    def test_get_u2ftokens_without_params(self):
        """ Test to get u2ftokens without params.
        """
        response = list(self.client_list.get_u2ftokens())[0]
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'GET')
        self.assertEqual(uri, '/admin/v1/u2ftokens')
        self.assertEqual(util.params_to_dict(args),
                         {'account_id':[self.client_list.account_id]})

    def test_get_u2ftoken_by_id(self):
        """ Test to get u2ftoken by registration id.
        """
        response = self.client.get_u2ftoken_by_id('DU012345678901234567')
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'GET')
        self.assertEqual(uri, '/admin/v1/u2ftokens/DU012345678901234567')
        self.assertEqual(util.params_to_dict(args),
                         {'account_id':[self.client.account_id]})

    def test_delete_u2ftoken(self):
        """ Test to delete u2ftoken by registration id.
        """
        response = self.client.delete_u2ftoken('DU012345678901234567')
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'DELETE')
        self.assertEqual(uri, '/admin/v1/u2ftokens/DU012345678901234567')
        self.assertEqual(util.params_to_dict(args),
                         {'account_id':[self.client.account_id]})

    def test_get_user_bypass_codes(self):
        """ Test to get bypass codes by user id.
        """
        response = self.client.get_user_bypass_codes('DU012345678901234567')
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'GET')
        self.assertEqual(
            uri,
            '/admin/v1/users/DU012345678901234567/bypass_codes')
        self.assertEqual(util.params_to_dict(args),
                         {'account_id': [self.client.account_id]})

    def test_get_bypass_codes(self):
        """ Test to get bypass codes.
        """
        response = list(self.client_list.get_bypass_codes())[0]
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'GET')
        self.assertEqual(uri, '/admin/v1/bypass_codes')
        self.assertEqual(util.params_to_dict(args),
                         {'account_id': [self.client_list.account_id]})

    def test_delete_bypass_code_by_id(self):
        """ Test to delete a bypass code by id.
        """
        response = self.client.delete_bypass_code_by_id('DU012345678901234567')
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'DELETE')
        self.assertEqual(uri, '/admin/v1/bypass_codes/DU012345678901234567')
        self.assertEqual(util.params_to_dict(args),
                         {'account_id': [self.client.account_id]})

if __name__ == '__main__':
    unittest.main()
