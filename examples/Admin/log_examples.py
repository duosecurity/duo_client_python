#!/usr/bin/env python
import csv
import sys
from datetime import datetime, timedelta, timezone

import duo_client

argv_iter = iter(sys.argv[1:])


def get_next_arg(prompt, default=None):
    try:
        return next(argv_iter)
    except StopIteration:
        return input(prompt) or default


today = datetime.now(tz=timezone.utc)
default_mintime = int((today - timedelta(days=180)).timestamp())
default_maxtime = int(today.timestamp() * 1000) - 120

# Configuration and information about objects to create.
admin_api = duo_client.Admin(
    ikey=get_next_arg("Admin API integration key: "),
    skey=get_next_arg("Integration secret key: "),
    host=get_next_arg("API hostname: "),
)
params = {}

mintime = get_next_arg("Mintime: ", default_mintime)
if mintime:
    params["mintime"] = mintime

maxtime = get_next_arg("Maxtime: ", default_maxtime)
if maxtime:
    params["maxtime"] = maxtime

limit = get_next_arg("Limit (1000): ")
if limit:
    params["limit"] = limit

next_offset = get_next_arg("Next_offset: ")
if next_offset:
    params["next_offset"] = next_offset

sort = get_next_arg("Sort (ts:desc): ")
if sort:
    params["sort"] = sort

log_type = get_next_arg("Log Type (telephony_v2): ", "telephony_v2")
print(f"Fetching {log_type} logs...")
reporter = csv.writer(sys.stdout)

print("==============================")
if log_type == "activity":
    params["mintime"] = params["mintime"] * 1000
    activity_logs = admin_api.get_activity_logs(**params)
    print(
        "Next offset from response: ", activity_logs.get("metadata").get("next_offset")
    )
    reporter.writerow(
        ("activity_id", "ts", "action", "actor_name", "target_name", "application")
    )
    for log in activity_logs["items"]:
        activity = log["activity_id"]
        ts = log["ts"]
        action = log["action"]
        actor_name = log.get("actor", {}).get("name", None)
        target_name = log.get("target", {}).get("name", None)
        application = log.get("application", {}).get("name", None)
        reporter.writerow(
            [
                activity,
                ts,
                action,
                actor_name,
                target_name,
                application,
            ]
        )
if log_type == "telephony_v2":
    telephony_logs = admin_api.get_telephony_log(api_version=2, kwargs=params)
    reporter.writerow(("telephony_id", "txid", "credits", "context", "phone", "type"))
    
    for log in telephony_logs["items"]:
        telephony_id = log["telephony_id"]
        txid = log["txid"]
        credits = log["credits"]
        context = log["context"]
        phone = log["phone"]
        type = log["type"]
        reporter.writerow(
            [
                telephony_id,
                txid,
                credits,
                context,
                phone,
                type
            ]
        )
if log_type == "auth":
    auth_logs = admin_api.get_authentication_log(api_version=2, kwargs=params)
    print(
        "Next offset from response: ",
        auth_logs.get("metadata").get("next_offset"),
    )
    reporter.writerow(("admin", "akey", "context", "phone", "provider"))
    for log in auth_logs["authlogs"]:
        admin = log["admin_name"]
        akey = log["akey"]
        context = log["context"]
        phone = log["phone"]
        provider = log["provider"]
        reporter.writerow(
            [
                admin,
                akey,
                context,
                phone,
                provider,
            ]
        )

print("==============================")
