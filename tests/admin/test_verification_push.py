import json
from .. import util
from .base import TestAdmin


class TestVerificationPush(TestAdmin):
    def test_send_verification_push(self):
        """
        Test sending a verification push to a user.
        """
        response = self.client.send_verification_push('test_user_id', 'test_phone_id')
        self.assertEqual(response['method'], 'POST')
        self.assertEqual(response['uri'],
                         '/admin/v1/users/test_user_id/send_verification_push')
        self.assertEqual(
           json.loads(response['body']),
            {'phone_id': 'test_phone_id', 'account_id': self.client.account_id})

    def test_get_verification_push_response(self):
        """
        Test getting the verification push response.
        """
        response = self.client.get_verification_push_response('test_user_id', 'test_push_id')
        (uri, args) = response['uri'].split('?')
        self.assertEqual(response['method'], 'GET')
        self.assertEqual(uri, '/admin/v1/users/test_user_id/verification_push_response')

        self.assertEqual(
            util.params_to_dict(args),
            {'push_id': ['test_push_id'], 'account_id': [self.client.account_id]})
