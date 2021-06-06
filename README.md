# centralized_rate_limiter
centralized redis backed rate limiter


## why a custom rate limiter?
i was unhappy with "edge" rate limiters because they lacked "context" (they were keyed to ip) and the out of the recommended django and flask rate limiters because they fall short when used in environments with "load balanced" servers.


## properties:
- allows for custom keys: you can provide as many "keys" as you need.
- centralized: you can have all of the servers using this rate limiter connect to one instance of redis.
- atomic: both rate limiters make use of transactions to ensure atomicity and preventing race conditions when interfacing with redis.


## what is the difference between "fixed" and "sliding" windows?
*tl;dr* fixed window is susceptible to request "spikes" and sliding window is not.

fixed window checks to make sure that there are less than "limit" requests in a static window "period". that is, with a limit of x and a period of y the rate limiter checks that there were less than x requests issued in time*y.

sliding window checks the make sure that there are less than "limit" requests issued in the last "period" size window. that is, with a limit of x and a period of y the rate limiter checks that there have been less than x requests in the last y time.


## recommendations:
- centralize where possible: synching distributed caches is a complicated problem that often results in inconsistencies. where possible you should try to use a centralized cache. i recommend considering a centralized cache for infrequently accessed sensitive functionality (ex. login, mfa, registration, password reset).
- use multiple unique keys where possible: more than one unique "key" could help you identify potentially malicious requests (ex. ip, user id, and device fingerprint). 
- prudently choose your keys: too many keys will result in latency, not enough keys will make sure 
- understand your "persistence" requirements: if you need "persistence" you shouldn't go with a cache based rate limiter. for example, if users verify their bank account through the microtransaction pattern you should leverage a database instead of a cache.
- log decisions: if you use this rate limiter you should ensure that you are logging the "decisions" that were made. logging this information will help you identify malicious activity. 
- set a "max length" on your keys: if the “key” for the lookup is based on user input you should set a “max” length. the “max” is to prevent malicious actors from setting a large “key” that would affect lookup times.


## references: 
- https://blog.cloudflare.com/counting-things-a-lot-of-different-things	
- https://konghq.com/blog/how-to-design-a-scalable-rate-limiting-algorithm/
- https://hechao.li/2018/06/25/rate-limiter-part1/
- https://engineering.classdojo.com/blog/2015/02/06/rolling-rate-limiter/
- https://github.com/astagi/python-limit-requests
- https://www.linkedin.com/pulse/resources-rate-limit-api-security-owasp-api42019-ali/
- https://realpython.com/python-redis/
