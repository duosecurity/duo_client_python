import json
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
            json.loads(response['body']),
            {
                'account_id': self.client.account_id,
                'has_external_password_mgmt': 'False'
            })

    def test_update_admin_password_mgmt_status_set_password(self):
        response = self.client_list.update_admin_password_mgmt_status(
            'DFAKEADMINID', has_external_password_mgmt='True', password='dolphins')
        response = response[0]
        self.assertEqual(response['method'], 'POST')
        self.assertEqual(response['uri'], '/admin/v1/admins/DFAKEADMINID/password_mgmt')
        self.assertEqual(
            json.loads(response['body']),
            {
                'account_id': self.client.account_id,
                'has_external_password_mgmt': 'True',
                'password': 'dolphins'
            })

    def test_create_admin(self):
        response = self.client.add_admin('test-name', 'test-email', 'test-phone', 'test-pswd')
        self.assertEqual(response['method'], 'POST')
        self.assertEqual(response['uri'], '/admin/v1/admins')
        self.assertEqual(
            json.loads(response['body']),
            {
                'account_id': self.client.account_id,
                'name': 'test-name',
                'email': 'test-email',
                'phone': 'test-phone',
            })

    def test_create_admin_with_role(self):
        response = self.client.add_admin('test-name', 'test-email', 'test-phone', 'test-pswd', 'test-role')
        self.assertEqual(response['method'], 'POST')
        self.assertEqual(response['uri'], '/admin/v1/admins')
        self.assertEqual(
            json.loads(response['body']),
            {
                'account_id': self.client.account_id,
                'name': 'test-name',
                'email': 'test-email',
                'phone': 'test-phone',
                'role': 'test-role',
            })

    def test_create_admin_with_subaccount_role(self):
        response = self.client.add_admin('test-name', 'test-email', 'test-phone', 'test-pswd', 'test-role', 'test-subaccount-role')
        self.assertEqual(response['method'], 'POST')
        self.assertEqual(response['uri'], '/admin/v1/admins')
        self.assertEqual(
            json.loads(response['body']),
            {
                'account_id': self.client.account_id,
                'name': 'test-name',
                'email': 'test-email',
                'phone': 'test-phone',
                'role': 'test-role',
                'subaccount_role': 'test-subaccount-role',
            })

    def test_update_admin_pass_all_params(self):
        response = self.client.update_admin('test-id', 'test-name1', 'test-phone', None, False, 'test-status', 'test-role', 'test-subaccount-role')
        self.assertEqual(response['method'], 'POST')
        self.assertEqual(response['uri'], '/admin/v1/admins/test-id')
        self.assertEqual(
            json.loads(response['body']),
            {
                'account_id': self.client.account_id,
                'name': 'test-name1',
                'password_change_required': False,
                'phone': 'test-phone',
                'role': 'test-role',
                'status': 'test-status',
                'subaccount_role': 'test-subaccount-role',
            })
        
    def test_update_admin_pass_two_optional_params(self):
        response = self.client.update_admin(admin_id='test-id', name='test-name2', status='test-status')
        self.assertEqual(response['method'], 'POST')
        self.assertEqual(response['uri'], '/admin/v1/admins/test-id')
        self.assertEqual(
            json.loads(response['body']),
            {
                'account_id': self.client.account_id,
                'name': 'test-name2',
                'status': 'test-status',
            })
    
    def test_update_admin_pass_one_optional_param(self):
        response = self.client.update_admin(admin_id='test-id', name='test-name3')
        self.assertEqual(response['method'], 'POST')
        self.assertEqual(response['uri'], '/admin/v1/admins/test-id')
        self.assertEqual(
            json.loads(response['body']),
            {
                'account_id': self.client.account_id,
                'name': 'test-name3',
            })
