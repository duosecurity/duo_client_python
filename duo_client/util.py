from typing import Dict, Sequence, Tuple
from datetime import datetime, timedelta, timezone


def get_params_from_kwargs(valid_params: Sequence[str], **kwargs) -> Dict:
    params = {}
    for k in kwargs:
        if kwargs[k] is not None and k in valid_params:
            params[k] = kwargs[k]
    return params


def get_log_uri(log_type: str, version: int = 1) -> str:
    return f"/admin/v{version}/logs/{log_type}"


def get_default_request_times() -> Tuple[int, int]:
    today = datetime.now(tz=timezone.utc)
    mintime = int((today - timedelta(days=180)).timestamp() * 1000)
    maxtime = int(today.timestamp() * 1000) - 120
    return mintime, maxtime
