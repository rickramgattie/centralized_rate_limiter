import time
from datetime import timedelta

import logger
import redis
from redis import Redis


# Fixed Window
def fixed_window_max_requests_per_seconds(
    r: Redis, keys: list, limit: int, period: timedelta
):
    return_value = True  # Fails closed
    for key in keys:
        if r.setnx(key, limit):  # If key does not exist, set it.
            r.expire(key, int(period.total_seconds()))
        with r.pipeline() as pipe:  # Use a transaction
            try:
                pipe.watch(
                    key
                )  # Raise an exception is the key value is updated externally
                attempts_left = r.get(key)
                if attempts_left and (int(attempts_left) > 0):
                    pipe.multi()
                    pipe.decrby(key, 1)
                    pipe.execute()
                    return_value &= False
                else:
                    pipe.unwatch()
                    return_value &= True
            except redis.WatchError:
                logger.info(f"There was a watch error for {key}")
    return return_value


# Sliding Window
def sliding_window_max_requests_per_seconds(
    r: Redis, keys: list, limit: int, period: timedelta
):
    return_value = True  # Fails closed
    total_seconds = int(period.total_seconds())
    for key in keys:
        with r.pipeline() as pipe:  # Use a transaction and the "set-then-get" pattern
            try:
                pipe.watch(
                    key
                )  # Raise an exception is the key value is updated externally
                current_time = float(time.time())
                pipe.multi()
                pipe.zadd(key, {current_time: current_time})
                pipe.zremrangebyscore(key, float("-inf"), current_time - total_seconds)
                pipe.expire(
                    key, total_seconds
                )  # Update the expiry to size window after the last request
                pipe.execute()
                total_requests = r.zcount(key, float("-inf"), float("+inf"))
            except redis.WatchError:
                logger.info(f"There was a watch error for {key}")
        return_value &= True if total_requests > limit else False
    return return_value


## EXAMPLE FIXED WINDOW CALLER
# r = redis.Redis(host="localhost", port=6379, db=0)
# requests = 30
# for i in range(requests):
#    if max_requests_per_seconds(
#        r=r,
#        keys=["ratelimit:<ip>", "ratelimit:<username>"],
#        limit=10,
#        period=timedelta(seconds=30),
#    ):
#        print("🔴 Request is not allowed")
#    else:
#        print("🟢 Request is allowed")

## EXAMPLE SLIDING WINDOW CALLER
# r = redis.Redis(host="localhost", port=6379, db=1)
# requests = 30
# for i in range(requests):
#    if fixed_window_max_requests_per_seconds(
#        r=r,
#        keys=["ratelimit:<ip>", "ratelimit:<username>"],
#        limit=10,
#        period=timedelta(seconds=30)
#    ):
#        print("🔴 Request is not allowed")
#    else:
#        print("🟢 Request is allowed")
