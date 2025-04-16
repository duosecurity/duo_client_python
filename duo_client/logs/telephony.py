from typing import Callable
from duo_client.util import (
    get_params_from_kwargs,
    get_log_uri,
    get_default_request_times,
)

VALID_TELEPHONY_V2_REQUEST_PARAMS = [
    "filters",
    "mintime",
    "maxtime",
    "limit",
    "sort",
    "next_offset",
    "account_id",
]

LOG_TYPE = "telephony"


class Telephony:
    @staticmethod
    def get_telephony_logs_v1(json_api_call: Callable, host: str, mintime=0):
        # Sanity check mintime as unix timestamp, then transform to string
        mintime = f"{int(mintime)}"
        params = {
            "mintime": mintime,
        }
        response = json_api_call(
            "GET",
            get_log_uri(LOG_TYPE, 1),
            params,
        )
        for row in response:
            row["eventtype"] = LOG_TYPE
            row["host"] = host
        return response

    @staticmethod
    def get_telephony_logs_v2(json_api_call: Callable, host: str, **kwargs):
        params = {}
        default_mintime, default_maxtime = get_default_request_times()

        params = get_params_from_kwargs(VALID_TELEPHONY_V2_REQUEST_PARAMS, **kwargs)

        if "mintime" not in params:
            # If mintime is not provided, the script defaults it to 180 days in past
            params["mintime"] = default_mintime
        params["mintime"] = f"{int(params['mintime'])}"
        if "maxtime" not in params:
            # if maxtime is not provided, the script defaults it to now
            params["maxtime"] = default_maxtime
        params["maxtime"] = f"{int(params['maxtime'])}"
        if "limit" in params:
            params["limit"] = f"{int(params['limit'])}"

        response = json_api_call(
            "GET",
            get_log_uri(LOG_TYPE, 2),
            params,
        )
        for row in response["items"]:
            row["eventtype"] = LOG_TYPE
            row["host"] = host
        return response
