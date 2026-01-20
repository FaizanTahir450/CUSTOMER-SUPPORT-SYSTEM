# security/rate_limiter.py
import time
from collections import defaultdict

class RateLimiter:
    """
    Simple in-memory rate limiter.
    """

    LIMITS = {
        "/api/query": (10, 60),     # 10 requests per 60 seconds
        "/api/schema": (5, 60),
        "/api/tables": (5, 60),
        "/api/execute-sql": (5, 60),
    }

    def __init__(self):
        self.clients = defaultdict(list)

    def check(self, client_id: str, endpoint: str) -> None:
        if endpoint not in self.LIMITS:
            return  # No limit for unspecified endpoints

        limit, window = self.LIMITS[endpoint]
        now = time.time()

        timestamps = self.clients[(client_id, endpoint)]
        timestamps = [t for t in timestamps if now - t < window]

        if len(timestamps) >= limit:
            raise ValueError("Rate limit exceeded. Please slow down.")

        timestamps.append(now)
        self.clients[(client_id, endpoint)] = timestamps
