from .. import util
import duo_client.admin
from .base import TestAdmin


class TestUserTokens(TestAdmin):
    def test_get_user_tokens_iterator(self):
        """ Test to get tokens iterator by user id.
        """
        generator = self.client_list.get_user_tokens_iterator(
            'DU012345678901234567')
        response = next(generator)
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'GET')
        self.assertEqual(uri, '/admin/v1/users/DU012345678901234567/tokens')
        self.assertEqual(util.params_to_dict(args),
                         {
                            'account_id':[self.client.account_id],
                            'limit': ['100'],
                            'offset': ['0'],
                        })

    def test_get_user_tokens(self):
        """ Test to get tokens by user id.
        """
        response = self.client_list.get_user_tokens('DU012345678901234567')[0]
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'GET')
        self.assertEqual(uri, '/admin/v1/users/DU012345678901234567/tokens')
        self.assertEqual(util.params_to_dict(args),
                         {
                            'account_id':[self.client.account_id],
                            'limit': ['100'],
                            'offset': ['0'],
                        })

    def test_get_user_tokens_offset(self):
        """ Test to get tokens by user id with pagination params.
        """
        response = self.client_list.get_user_tokens(
            'DU012345678901234567', offset=100)[0]
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'GET')
        self.assertEqual(uri, '/admin/v1/users/DU012345678901234567/tokens')
        self.assertEqual(util.params_to_dict(args),
                         {
                            'account_id':[self.client.account_id],
                            'limit': ['100'],
                            'offset': ['0'],
                        })

    def test_get_user_tokens_limit(self):
        """ Test to get tokens by user id with pagination params.
        """
        response = self.client_list.get_user_tokens(
            'DU012345678901234567', limit=500)[0]
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'GET')
        self.assertEqual(uri, '/admin/v1/users/DU012345678901234567/tokens')
        self.assertEqual(util.params_to_dict(args),
                         {
                            'account_id':[self.client.account_id],
                            'limit': ['500'],
                            'offset': ['0'],
                        })

    def test_get_user_tokens_limit_and_offset(self):
        """ Test to get tokens by user id with pagination params.
        """
        response = self.client_list.get_user_tokens(
            'DU012345678901234567', limit=10, offset=100)[0]
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'GET')
        self.assertEqual(uri, '/admin/v1/users/DU012345678901234567/tokens')
        self.assertEqual(util.params_to_dict(args),
                         {
                            'account_id':[self.client.account_id],
                            'limit': ['10'],
                            'offset': ['100'],
                        })


if __name__ == '__main__':
    unittest.main()
