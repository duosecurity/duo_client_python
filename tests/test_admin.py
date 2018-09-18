from __future__ import absolute_import
import unittest
import warnings
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

        # if you are wanting to get a response from a call to get
        # authentication logs
        self.client_authlog = duo_client.admin.Admin(
            'test_ikey', 'test_akey', 'example.com')
        self.client_authlog.account_id = 'DA012345678901234567'
        self.client_authlog._connect = \
            lambda: util.MockHTTPConnection(data_response_from_get_authlog=True)

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
        response = self.client.add_user(
            'foo', realname='bar', status='active', notes='notes',
            email='foobar@baz.com', firstname='fName', lastname='lName',
            alias1='alias1', alias2='alias2', alias3='alias3', alias4='alias4')
        self.assertEqual(response['method'], 'POST')
        self.assertEqual(response['uri'], '/admin/v1/users')
        self.assertEqual(
            util.params_to_dict(response['body']),
            {
                'realname': ['bar'],
                'notes': ['notes'],
                'username': ['foo'],
                'status': ['active'],
                'email': ['foobar%40baz.com'],
                'firstname': ['fName'],
                'lastname': ['lName'],
                'account_id': [self.client.account_id],
                'alias1': ['alias1'],
                'alias2': ['alias2'],
                'alias3': ['alias3'],
                'alias4': ['alias4'],
            })
        # defaults
        response = self.client.add_user('bar')
        self.assertEqual(response['method'], 'POST')
        self.assertEqual(response['uri'], '/admin/v1/users')
        self.assertEqual(
            util.params_to_dict(response['body']),
            {'username':['bar'], 'account_id':[self.client.account_id]})

    def test_update_user(self):
        response = self.client.update_user(
            'DU012345678901234567', username='foo', realname='bar',
            status='active', notes='notes', email='foobar@baz.com',
            firstname='fName', lastname='lName', alias1='alias1',
            alias2='alias2', alias3='alias3', alias4='alias4')
        self.assertEqual(response['method'], 'POST')
        self.assertEqual(
            response['uri'], '/admin/v1/users/DU012345678901234567')
        self.assertEqual(
            util.params_to_dict(response['body']),
            {
                'account_id':[self.client.account_id],
                'realname': ['bar'],
                'notes': ['notes'],
                'username': ['foo'],
                'status': ['active'],
                'email': ['foobar%40baz.com'],
                'firstname': ['fName'],
                'lastname': ['lName'],
                'account_id': [self.client.account_id],
                'alias1': ['alias1'],
                'alias2': ['alias2'],
                'alias3': ['alias3'],
                'alias4': ['alias4'],
            })

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

    def test_get_authentication_log_v1(self):
        """ Test to get authentication log on version 1 api.
        """
        response = self.client_list.get_authentication_log(api_version=1)[0]
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'GET')
        self.assertEqual(uri, '/admin/v1/logs/authentication')
        self.assertEqual(
            util.params_to_dict(args)['account_id'],
            [self.client_list.account_id])

    def test_get_authentication_log_v2(self):
        """ Test to get authentication log on version 1 api.
        """
        response = self.client_authlog.get_authentication_log(api_version=2)
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'GET')
        self.assertEqual(uri, '/admin/v2/logs/authentication')
        self.assertEqual(
            util.params_to_dict(args)['account_id'],
            [self.client_authlog.account_id])

    def test_get_groups(self):
        """ Test for getting list of all groups
        """
        response = self.client.get_groups()
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'GET')
        self.assertEqual(uri, '/admin/v1/groups')
        self.assertEqual(util.params_to_dict(args),
                         {'account_id': [self.client.account_id]})

    def test_get_group_v1(self):
        """ Test for v1 API of getting specific group details
        """
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            response = self.client.get_group('ABC123', api_version=1)
            uri, args = response['uri'].split('?')

            # Assert deprecation warning generated
            self.assertEqual(len(w), 1)
            self.assertTrue(issubclass(w[0].category, DeprecationWarning))
            self.assertIn('Please migrate to the v2 API', str(w[0].message))

            self.assertEqual(response['method'], 'GET')
            self.assertEqual(uri, '/admin/v1/groups/ABC123')
            self.assertEqual(util.params_to_dict(args),
                             {'account_id': [self.client.account_id]})

    def test_get_group_v2(self):
        """ Test for v2 API of getting specific group details
        """
        response = self.client.get_group('ABC123', api_version=2)
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'GET')
        self.assertEqual(uri, '/admin/v2/groups/ABC123')
        self.assertEqual(util.params_to_dict(args),
                         {'account_id': [self.client.account_id]})

    def test_get_group_users(self):
        """ Test for getting list of users associated with a group
        """
        response = self.client.get_group_users('ABC123')
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'GET')
        self.assertEqual(uri, '/admin/v2/groups/ABC123/users')
        self.assertEqual(
            util.params_to_dict(args),
            {
                'account_id': [self.client.account_id],
                'limit': ['100'],
                'offset': ['0'],
            })

    def test_delete_group(self):
        """ Test for deleting a group
        """
        response = self.client.delete_group('ABC123')
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'DELETE')
        self.assertEqual(uri, '/admin/v1/groups/ABC123')
        self.assertEqual(util.params_to_dict(args),
                         {'account_id': [self.client.account_id]})

    def test_modify_group(self):
        """ Test for modifying a group
        """
        response = self.client.modify_group('ABC123')
        self.assertEqual(response['method'], 'POST')
        self.assertEqual(response['uri'], '/admin/v1/groups/ABC123')
        self.assertEqual(util.params_to_dict(response['body']),
                         {'account_id': [self.client.account_id]})


if __name__ == '__main__':
    unittest.main()
