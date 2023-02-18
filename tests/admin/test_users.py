from .. import util
import duo_client.admin
from .base import TestAdmin


class TestUsers(TestAdmin):
    def test_get_users_generator(self):
        """ Test to get users iterator.
        """
        iterator = self.client_list.get_users_iterator()
        response = next(iterator)
        self.assertEqual(response['method'], 'GET')
        (uri, args) = response['uri'].split('?')
        self.assertEqual(uri, '/admin/v1/users')
        self.assertEqual(
            util.params_to_dict(args),
            {
                'account_id': [self.client.account_id],
                'limit': ['100'],
                'offset': ['0'],
            })

    def test_get_users(self):
        """ Test to get users.
        """
        response = self.client_list.get_users()[0]
        self.assertEqual(response['method'], 'GET')
        (uri, args) = response['uri'].split('?')
        self.assertEqual(uri, '/admin/v1/users')
        self.assertEqual(
            util.params_to_dict(args),
            {
                'account_id': [self.client.account_id],
                'limit': ['100'],
                'offset': ['0'],
            })

    def test_get_users_offset(self):
        """ Test to get users with pagination params.
        """
        response = self.client_list.get_users(offset=30)[0]
        self.assertEqual(response['method'], 'GET')
        (uri, args) = response['uri'].split('?')
        self.assertEqual(uri, '/admin/v1/users')
        self.assertEqual(
            util.params_to_dict(args),
            {
                'account_id': [self.client.account_id],
                'limit': ['100'],
                'offset': ['0'],
            })

    def test_get_users_limit(self):
        """ Test to get users with pagination params.
        """
        response = self.client_list.get_users(limit=30)[0]
        self.assertEqual(response['method'], 'GET')
        (uri, args) = response['uri'].split('?')
        self.assertEqual(uri, '/admin/v1/users')
        self.assertEqual(
            util.params_to_dict(args),
            {
                'account_id': [self.client.account_id],
                'limit': ['30'],
                'offset': ['0'],
            })

    def test_get_users_limit_and_offset(self):
        """ Test to get users with pagination params.
        """
        response = self.client_list.get_users(limit=20, offset=30)[0]
        self.assertEqual(response['method'], 'GET')
        (uri, args) = response['uri'].split('?')
        self.assertEqual(uri, '/admin/v1/users')
        self.assertEqual(
            util.params_to_dict(args),
            {
                'account_id': [self.client.account_id],
                'limit': ['20'],
                'offset': ['30'],
            })

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
                'email': ['foobar@baz.com'],
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
                'email': ['foobar@baz.com'],
                'firstname': ['fName'],
                'lastname': ['lName'],
                'account_id': [self.client.account_id],
                'alias1': ['alias1'],
                'alias2': ['alias2'],
                'alias3': ['alias3'],
                'alias4': ['alias4'],
            })

    def test_sync_user(self):
        """ Test to synchronize a single user in a directory for a username.
        """
        response = self.client.sync_user('foo', 'test_dir_key')
        self.assertEqual(response['method'], 'POST')
        self.assertEqual(response['uri'],
                         '/admin/v1/users/directorysync/test_dir_key/syncuser')
        self.assertEqual(
            util.params_to_dict(response['body']),
            {'username': ['foo'], 'account_id': [self.client.account_id]})
