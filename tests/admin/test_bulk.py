import json

from .base import TestAdmin


class TestBulkOperations(TestAdmin):
    def test_bulk_add_users(self):
        """Test to bulk create users
        """
        response = self.client_list.bulk_add_users(
                [{"username": "example_username_1", "email": "example_user_1@example.com"},
                 {"username": "example_username_2", "status": "disabled"}, ])

        result_list = json.loads(json.loads(response[0]['body'])['users'])

        self.assertEqual(result_list[0]['username'], 'example_username_1')
        self.assertEqual(result_list[0]['email'], 'example_user_1@example.com')

    def test_bulk_operations(self):
        """Test to execute bulk operations
        """

        input_data = [{"method": "POST", "path": "/admin/v1/users",
                       "body":   {"username": "uname1", "alias1": "my_alias1", "alias2": "my_alias2",
                                  "alias3":   "my_alias3", "alias4": "my_alias4", "email": "user@example.com",
                                  "status":   "active", "notes": "This is a user", }, },
                      {"method": "POST", "path": "/admin/v1/users/DUXXXXXXXXXXXXXXXXXX",
                       "body":   {"alias2": "updated_alias2", "email": "user2@example.com", "status": "active",
                                  "notes":  "This is another user", }, },
                      {"method": "DELETE", "path": "/admin/v1/users/DUXXXXXXXXXXXXXXXXXX", "body": {}, },
                      {"method": "POST", "path": "/admin/v1/users/DUXXXXXXXXXXXXXXXXXX/groups",
                       "body":   {"group_id": "DUXXXXXXXXXXXXXXXXXX", }, },
                      {"method": "DELETE", "path": "/admin/v1/users/DUXXXXXXXXXXXXXXXXXX/groups/DUXXXXXXXXXXXXXXXXXX",
                       "body":   {}, }, ]
        response = self.client_list.bulk_operations(input_data)

        result_list = json.loads(json.loads(response[0]['body'])['operations'])
        self.assertEqual(result_list, input_data)
