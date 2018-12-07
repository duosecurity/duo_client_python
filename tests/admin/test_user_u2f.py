from .. import util
import duo_client.admin
from .base import TestAdmin


class TestUserU2F(TestAdmin):
    def test_get_user_u2ftokens(self):
        """ Test to get u2ftokens by user id.
        """
        response = self.client.get_user_u2ftokens('DU012345678901234567')
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'GET')
        self.assertEqual(uri, '/admin/v1/users/DU012345678901234567/u2ftokens')
        self.assertEqual(util.params_to_dict(args),
                         {'account_id':[self.client.account_id]})
