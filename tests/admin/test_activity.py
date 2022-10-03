from .. import util
from .base import TestAdmin


class TestEndpoints(TestAdmin):

    def test_get_activity_log(self):
        """ Test to get activities log.
        """
        response = self.client_activity.get_activity_logs(maxtime='1663131599000', mintime='1662958799000')
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'GET')
        self.assertEqual(uri, '/admin/v2/logs/activity')
        self.assertEqual(
            util.params_to_dict(args)['account_id'],
            [self.client_activity.account_id])

    def test_get_activity_log_with_no_args(self):
        """ Test to get activities log.
        """
        response = self.client_activity.get_activity_logs()
        uri, args = response['uri'].split('?')

        self.assertEqual(response['method'], 'GET')
        self.assertEqual(uri, '/admin/v2/logs/activity')
        self.assertEqual(
            util.params_to_dict(args)['account_id'],
            [self.client_activity.account_id])

