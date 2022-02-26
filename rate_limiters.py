from collections import defaultdict
from typing import List


class RateLimiter:
    # Should be called once per second
    def tick(self, current_time: int):
        pass

    def check(self, client_id: str) -> bool:
        return False


class FixedWindow(RateLimiter):
    def __init__(self):
        self.window = 5
        self.limit = 5
        self.counter = defaultdict(int)

    def tick(self, current_time: int):
        if self.window == 1 or current_time % self.window == 0:
            # Reset counters
            self.counter = defaultdict(int)

    def check(self, client_id: str) -> bool:
        allowed = self.counter[client_id] < self.limit
        if allowed:
            self.counter[client_id] += 1
        return allowed


class TokenBucketLimiter(RateLimiter):
    def __init__(self, clients: List[str]):
        super().__init__()
        self.window = 5
        self.limit = 5
        self.tokens = defaultdict(int)
        for client in clients:
            self.tokens[client] = 0
        self.last_time = -1

    def tick(self, current_time: int):
        if self.last_time == current_time:
            return
        self.last_time = current_time

        # Add one token per second
        for client_id in self.tokens:
            self.tokens[client_id] = min(self.limit, self.tokens[client_id] + 1)

    def check(self, client_id: str) -> bool:
        self.tokens[client_id] -= 1
        should_allow = self.tokens[client_id] >= 0
        self.tokens[client_id] = max(0, self.tokens[client_id])
        return should_allow
