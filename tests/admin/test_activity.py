from .. import util
from .base import TestAdmin
from datetime import datetime, timedelta
from freezegun import freeze_time
import pytz


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

    @freeze_time('2022-10-01')
    def test_get_activity_log_with_no_args(self):
        freezed_time = datetime(2022,10,1,0,0,0, tzinfo=pytz.utc)
        expected_mintime = str(int((freezed_time-timedelta(days=180)).timestamp()*1000))
        expected_maxtime = str(int(freezed_time.timestamp() * 1000))
        response = self.client_activity.get_activity_logs()
        uri, args = response['uri'].split('?')
        param_dict = util.params_to_dict(args)
        self.assertEqual(response['method'], 'GET')
        self.assertEqual(uri, '/admin/v2/logs/activity')
        self.assertEqual(
            param_dict['mintime'],
            [expected_mintime])
        self.assertEqual(
            param_dict['maxtime'],
            [expected_maxtime])
