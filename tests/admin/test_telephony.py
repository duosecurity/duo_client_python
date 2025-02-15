from .. import util
from .base import TestAdmin
from datetime import datetime, timedelta
from freezegun import freeze_time
import pytz


class TestTelephonyLogEndpoints(TestAdmin):
    def test_get_telephony_logs_v2(self):
        """Test to get activities log."""
        response = self.items_response_client.get_telephony_log(
            maxtime=1663131599000, mintime=1662958799000, api_version=2
        )
        uri, args = response["uri"].split("?")

        self.assertEqual(response["method"], "GET")
        self.assertEqual(uri, "/admin/v2/logs/telephony")
        self.assertEqual(
            util.params_to_dict(args)["account_id"], [self.items_response_client.account_id]
        )

    @freeze_time("2022-10-01")
    def test_get_telephony_logs_v2_no_args(self):
        freezed_time = datetime(2022, 10, 1, 0, 0, 0, tzinfo=pytz.utc)
        expected_mintime = str(
            int((freezed_time - timedelta(days=180)).timestamp() * 1000)
        )
        expected_maxtime = str(int(freezed_time.timestamp() * 1000) - 120)
        response = self.items_response_client.get_telephony_log(api_version=2)
        uri, args = response["uri"].split("?")
        param_dict = util.params_to_dict(args)
        self.assertEqual(response["method"], "GET")
        self.assertEqual(uri, "/admin/v2/logs/telephony")
        self.assertEqual(param_dict["mintime"], [expected_mintime])
        self.assertEqual(param_dict["maxtime"], [expected_maxtime])
        self.assertAlmostEqual(param_dict["sort"], ["ts:desc"])
        self.assertEqual(param_dict["limit"], ["100"])

    @freeze_time("2022-10-01")
    def test_get_telephony_logs_v2_with_args(self):
        mintime = datetime(2022, 9, 1, 0, 0, 0, tzinfo=pytz.utc)
        expected_mintime = str(int(mintime.timestamp() * 1000))
        maxtime = datetime(2022, 10, 1, 0, 0, 0, tzinfo=pytz.utc)
        expected_maxtime = str(int(maxtime.timestamp() * 1000) - 120)
        params = {"mintime": expected_mintime, "sort": "asc", "limit": 900}
        response = self.items_response_client.get_telephony_log(api_version=2, 
                                                                **params)
        uri, args = response["uri"].split("?")
        param_dict = util.params_to_dict(args)
        self.assertEqual(response["method"], "GET")
        self.assertEqual(uri, "/admin/v2/logs/telephony")
        self.assertEqual(param_dict["mintime"], [expected_mintime])
        self.assertEqual(param_dict["maxtime"], [expected_maxtime])
        self.assertEqual(param_dict["sort"], ["ts:asc"])  
        self.assertEqual(param_dict["limit"], ["900"])

    @freeze_time("2022-10-01")
    def test_get_telephony_logs_v2_with_unsupported_args(self):
        params = {
            "unsupported": "argument",
            "non_existent": "argument"
            }
        response = self.items_response_client.get_telephony_log(api_version=2, 
                                                                **params)
        uri, args = response["uri"].split("?")
        param_dict = util.params_to_dict(args)
        self.assertEqual(response["method"], "GET")
        self.assertEqual(uri, "/admin/v2/logs/telephony")
        self.assertNotIn("unsupported", param_dict)
        self.assertNotIn("non_existent", param_dict)

    @freeze_time("2022-10-01")
    def test_get_telephony_logs_v1_no_args(self):
        response = self.client_list.get_telephony_log()
        uri, args = response[0]["uri"].split("?")
        self.assertEqual(response[0]["method"], "GET")
        self.assertEqual(uri, "/admin/v1/logs/telephony")

    @freeze_time("2022-10-01")
    def test_get_telephony_logs_v1_with_args(self):
        freezed_time = datetime(2022, 9, 1, 0, 0, 0, tzinfo=pytz.utc)
        expected_mintime = str(
            int((freezed_time - timedelta(days=180)).timestamp())
        )
        response = self.client_list.get_telephony_log(mintime=expected_mintime)
        uri, args = response[0]["uri"].split("?")
        param_dict = util.params_to_dict(args)
        self.assertEqual(response[0]["method"], "GET")
        self.assertEqual(uri, "/admin/v1/logs/telephony")
        self.assertEqual(param_dict["mintime"], [expected_mintime])
    
    @freeze_time("2022-10-01")
    def test_get_telephony_logs_v1_ignore_v2_args(self):
        freezed_time = datetime(2022, 9, 1, 0, 0, 0, tzinfo=pytz.utc)
        expected_mintime = str(
            int((freezed_time - timedelta(days=180)).timestamp())
        )
        params = {"mintime": expected_mintime, "limit": 20, "sort": "ts:asc"}
        response = self.client_list.get_telephony_log(**params)
        uri, args = response[0]["uri"].split("?")
        param_dict = util.params_to_dict(args)
        self.assertEqual(response[0]["method"], "GET")
        self.assertEqual(uri, "/admin/v1/logs/telephony")
        self.assertEqual(param_dict["mintime"], [expected_mintime])
        self.assertNotIn(param_dict["limit"], ["limit"])
        self.assertNotIn(param_dict["sort"], ["sort"])