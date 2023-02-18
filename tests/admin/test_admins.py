from .. import util
import duo_client.admin
from .base import TestAdmin


class TestAdmins(TestAdmin):
    # Uses underlying paging
    def test_get_admins(self):
        response = self.client_list.get_admins()
        response = response[0]
        self.assertEqual(response['method'], 'GET')
        (uri, args) = response['uri'].split('?')
        self.assertEqual(uri, '/admin/v1/admins')
        self.assertEqual(
            util.params_to_dict(args),
            {
                'account_id': [self.client.account_id],
                'limit': ['100'],
                'offset': ['0'],
            })

    def test_get_admins_with_limit(self):
        response = self.client_list.get_admins(limit='20')
        response = response[0]
        self.assertEqual(response['method'], 'GET')
        (uri, args) = response['uri'].split('?')
        self.assertEqual(uri, '/admin/v1/admins')
        self.assertEqual(
            util.params_to_dict(args),
            {
                'account_id': [self.client.account_id],
                'limit': ['20'],
                'offset': ['0'],
            })

    def test_get_admins_with_limit_offset(self):
        response = self.client_list.get_admins(limit='20', offset='2')
        response = response[0]
        self.assertEqual(response['method'], 'GET')
        (uri, args) = response['uri'].split('?')
        self.assertEqual(uri, '/admin/v1/admins')
        self.assertEqual(
            util.params_to_dict(args),
            {
                'account_id': [self.client.account_id],
                'limit': ['20'],
                'offset': ['2'],
            })

    def test_get_admins_with_offset(self):
        response = self.client_list.get_admins(offset=9001)
        response = response[0]
        self.assertEqual(response['method'], 'GET')
        (uri, args) = response['uri'].split('?')
        self.assertEqual(uri, '/admin/v1/admins')
        self.assertEqual(
            util.params_to_dict(args),
            {
                'account_id': [self.client.account_id],
                'limit': ['100'],
                'offset': ['0'],
            })

    def test_get_admins_iterator(self):
        response = self.client_list.get_admins_iterator()
        response = next(response)
        self.assertEqual(response['method'], 'GET')
        (uri, args) = response['uri'].split('?')
        self.assertEqual(uri, '/admin/v1/admins')
        self.assertEqual(
            util.params_to_dict(args),
            {
                'account_id': [self.client.account_id],
                'limit': ['100'],
                'offset': ['0'],
            })

    def test_get_external_password_mgmt_statuses(self):

        response = self.client_list.get_external_password_mgmt_statuses()
        response = response[0]
        self.assertEqual(response['method'], 'GET')
        (uri, args) = response['uri'].split('?')
        self.assertEqual(uri, '/admin/v1/admins/password_mgmt')
        self.assertEqual(
            util.params_to_dict(args),
            {
                'account_id': [self.client.account_id],
                'limit': ['100'],
                'offset': ['0'],
            })

    def test_get_external_password_mgmt_statuses_with_limit(self):
        response = self.client_list.get_external_password_mgmt_statuses(
            limit='20')
        response = response[0]
        self.assertEqual(response['method'], 'GET')
        (uri, args) = response['uri'].split('?')
        self.assertEqual(uri, '/admin/v1/admins/password_mgmt')
        self.assertEqual(
            util.params_to_dict(args),
            {
                'account_id': [self.client.account_id],
                'limit': ['20'],
                'offset': ['0'],
            })

    def test_get_external_password_mgmt_statusesg_with_limit_offset(self):
        response = self.client_list.get_external_password_mgmt_statuses(
            limit='20', offset='2')
        response = response[0]
        self.assertEqual(response['method'], 'GET')
        (uri, args) = response['uri'].split('?')
        self.assertEqual(uri, '/admin/v1/admins/password_mgmt')
        self.assertEqual(
            util.params_to_dict(args),
            {
                'account_id': [self.client.account_id],
                'limit': ['20'],
                'offset': ['2'],
            })

    def test_get_external_password_mgmt_statuses_with_offset(self):
        response = self.client_list.get_external_password_mgmt_statuses(
            offset=9001)
        response = response[0]
        self.assertEqual(response['method'], 'GET')
        (uri, args) = response['uri'].split('?')
        self.assertEqual(uri, '/admin/v1/admins/password_mgmt')
        self.assertEqual(
            util.params_to_dict(args),
            {
                'account_id': [self.client.account_id],
                'limit': ['100'],
                'offset': ['0'],
            })

    def test_get_external_password_mgmt_status_for_admin(self):
        response = self.client_list.get_external_password_mgmt_status_for_admin(
            'DFAKEADMINID')
        response = response[0]
        self.assertEqual(response['method'], 'GET')
        (uri, args) = response['uri'].split('?')
        self.assertEqual(uri, '/admin/v1/admins/DFAKEADMINID/password_mgmt')
        self.assertEqual(
            util.params_to_dict(args),
            {
                'account_id': [self.client.account_id],
            })

    def test_update_admin_password_mgmt_status(self):
        response = self.client_list.update_admin_password_mgmt_status(
            'DFAKEADMINID', has_external_password_mgmt='False')
        response = response[0]
        self.assertEqual(response['method'], 'POST')
        self.assertEqual(response['uri'], '/admin/v1/admins/DFAKEADMINID/password_mgmt')
        self.assertEqual(
            util.params_to_dict(response['body']),
            {
                'account_id': [self.client.account_id],
                'has_external_password_mgmt': ['False']
            })

    def test_update_admin_password_mgmt_status_set_password(self):
        response = self.client_list.update_admin_password_mgmt_status(
            'DFAKEADMINID', has_external_password_mgmt='True', password='dolphins')
        response = response[0]
        self.assertEqual(response['method'], 'POST')
        self.assertEqual(response['uri'], '/admin/v1/admins/DFAKEADMINID/password_mgmt')
        self.assertEqual(
            util.params_to_dict(response['body']),
            {
                'account_id': [self.client.account_id],
                'has_external_password_mgmt': ['True'],
                'password': ['dolphins']
            })
