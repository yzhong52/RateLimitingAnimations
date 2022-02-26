from collections import defaultdict
from typing import List, Dict, Deque


class RateLimiter:
    # Should be called once per second
    def tick(self, current_time: int):
        pass

    def check(self, client_id: str, current_time: int) -> bool:
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

    def check(self, client_id: str, current_time: int) -> bool:
        allowed = self.counter[client_id] < self.limit
        if allowed:
            self.counter[client_id] += 1
        return allowed


class SlidingLog(RateLimiter):
    def __init__(self):
        self._logs = defaultdict(lambda: Deque[int]())
        self.window = 5
        self.limit = 5

    @property
    def logs(self) -> Dict[str, Deque[int]]:
        return self._logs

    def tick(self, current_time: int):
        for _, log in self.logs.items():
            if log and log[0] <= current_time - self.window:
                log.popleft()

    def check(self, client_id: str, current_time: int) -> bool:
        log = self.logs[client_id]
        if len(log) < self.limit:
            log.append(current_time)
            return True
        return False


class TokenBucket(RateLimiter):
    class Bucket:
        def __init__(self):
            self.last_refill_time = -2
            self.count = 0

    def __init__(self, clients: List[str]):
        super().__init__()

        # Every {window} seconds, we refill the bucket with {refill_tokens}
        self.refill_tokens = 2
        self.refill_window = 2

        self.limit = 5
        self._tokens = defaultdict(lambda: TokenBucket.Bucket())
        for client in clients:
            self._tokens[client] = TokenBucket.Bucket()

    @property
    def tokens(self) -> Dict[str, Bucket]:
        return self._tokens

    def _refill(self, current_time: int, client_id: str):
        bucket = self.tokens[client_id]
        refill_window_count = (current_time - bucket.last_refill_time) // self.refill_window
        bucket.count = min(
            bucket.count + refill_window_count * self.refill_tokens,
            self.limit
        )
        bucket.last_refill_time += refill_window_count * self.refill_tokens

    def tick(self, current_time: int):
        for client_id in self.tokens:
            self._refill(current_time, client_id)

    def check(self, client_id: str, current_time: int) -> bool:
        if self.tokens[client_id].count > 0:
            self.tokens[client_id].count -= 1
            return True
        return False
