#!/usr/bin/env python
import sys
import datetime
import duo_client


def get_activity_logs(admin_api, min_time, users):
    authlogs = []
    # Large amounts of duo users being requests, even if below the max
    # URI limit, will just return no results ... 50 at a time seems to work
    for i in range(0, len(users), 50):
        end = i+50
        if end >= len(users):
            end = len(users)
        print(f"Requesting Auth Call {i}-{end}/{len(users)}")
        # It is reccomended to set this to 30 or 60 if using
        # get_authentication_log that will return many pages of results
        admin_api._INITIAL_BACKOFF_WAIT_SECS = 32
        res = admin_api.get_authentication_log(
            users=users[i:end],
            limit="1000",
            mintime=datetime.datetime.timestamp(min_time)*1000
        )
        authlogs += list(res)
        print(f"Finished Auth Call {i}-{end}/{len(users)} - with {len(authlogs)} records")
    return authlogs


def get_next_arg(prompt):
    try:
        return next(argv_iter)
    except StopIteration:
        return input(prompt)


def main():
    admin_api = duo_client.Admin(
        ikey=get_next_arg('Admin API integration key ("DI..."): '),
        skey=get_next_arg('integration secret key: '),
        host=get_next_arg('API hostname ("api-....duosecurity.com"): '),
    )

    users = admin_api.get_users(limit=10)
    one_ago = datetime.datetime.now() - datetime.timedelta(days=1)
    bad_users = users

    bad_user_ids = [user['user_id'] for user in bad_users]
    print(bad_user_ids)
    act_logs = get_activity_logs(admin_api, one_ago, bad_user_ids)
    for act_log in act_logs:
        username = act_log['user']['name']
        security_agent = act_log['access_device']['security_agents']
        print(f"Found log for {username} running {security_agent}")

if __name__ == "__main__":
    argv_iter = iter(sys.argv[1:])
    main()
