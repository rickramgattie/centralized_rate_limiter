# centralized_rate_limiter
Centralized Redis Backed Rate Limiter


## Why a custom rate limiter?
I was unhappy with "edge" rate limiters because they lacked "context" (they were keyed to ip) and the out of the recommended Django and Flask rate limiters because they fall short when used in environments with "load balanced" servers.


## Properties:
- Allows for custom keys: You can provide as many "keys" as you need.
- Centralized: You can have all of the servers using this rate limiter connect to one instance of Redis.
- Atomic: Both rate limiters make use of transactions to ensure atomicity and preventing race conditions when interfacing with Redis.


## What is the difference between "fixed" and "sliding" windows?
*tl;dr* fixed window is susceptible to request "spikes" and sliding window is not.

Fixed window checks to make sure that there are less than "limit" requests in a static window "period". That is, with a limit of X and a period of Y the rate limiter checks that there were less than X requests issued in _time_*Y.

Sliding window checks the make sure that there are less than "limit" requests issued in the last "period" size window. That is, with a limit of X and a period of Y the rate limiter checks that there have been less than X requests in the last Y _time_.


## Recommendations:
- Centralize where possible: Synching distributed caches is a complicated problem that often results in inconsistencies. Where possible you should try to use a centralized cache. I recommend considering a centralized cache for infrequently accessed sensitive functionality (ex. login, mfa, registration, password reset).
- Use multiple unique keys where possible: More than one unique "key" could help you identify potentially malicious requests (ex. ip, user id, and device fingerprint). 
- Prudently choose your keys: Too many keys will result in latency, not enough keys will make the rate limiter innefective.
- Understand your "persistence" requirements: If you need "persistence" you shouldn't go with a cache based rate limiter. For example, if users verify their bank account through the microtransaction pattern you should leverage a database instead of a cache.
- Log decisions: If you use this rate limiter you should ensure that you are logging the "decisions" that were made. Logging this information will help you identify malicious activity. 
- Set a "max length" on your keys: If the “key” for the lookup is based on user input you should set a “max length." The “max” is to prevent malicious actors from setting a large “key” that would affect lookup times.


## References: 
- https://blog.cloudflare.com/counting-things-a-lot-of-different-things	
- https://konghq.com/blog/how-to-design-a-scalable-rate-limiting-algorithm/
- https://hechao.li/2018/06/25/rate-limiter-part1/
- https://engineering.classdojo.com/blog/2015/02/06/rolling-rate-limiter/
- https://github.com/astagi/python-limit-requests
- https://www.linkedin.com/pulse/resources-rate-limit-api-security-owasp-api42019-ali/
- https://realpython.com/python-redis/
