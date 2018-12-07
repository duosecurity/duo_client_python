from .. import util
import duo_client.admin
from .base import TestAdmin


class TestUsers(TestAdmin):
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
