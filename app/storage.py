import asyncio
import time
from typing import Callable, Dict, Optional, Tuple

try:
    from app.token_bucket import TokenBucket
except ImportError:
    class TokenBucket:
        def __init__(self, capacity: float, refill_rate: float, time_func: Optional[Callable[[], float]] = None) -> None:
            self.capacity = float(capacity)
            self.refill_rate = float(refill_rate)
            self.tokens = float(capacity)
            self.time_func = time_func or time.monotonic
            self.last_refill = self.time_func()

        def _refill(self, current_time: float) -> None:
            delta = max(0.0, current_time - self.last_refill)
            self.tokens = min(self.capacity, self.tokens + delta * self.refill_rate)
            self.last_refill = current_time

        def consume(self, tokens: float = 1.0, current_time: Optional[float] = None) -> Tuple[bool, float, float]:
            now = self.time_func() if current_time is None else current_time
            self._refill(now)
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True, self.tokens, 0.0
            deficit = tokens - self.tokens
            retry_after = deficit / self.refill_rate if self.refill_rate > 0 else float("inf")
            return False, self.tokens, retry_after

        def reset_time(self) -> float:
            deficit = self.capacity - self.tokens
            return deficit / self.refill_rate if self.refill_rate > 0 else 0.0


class InMemoryTokenBucketStore:
    """
    Thread-safe and async-safe in-memory storage manager for client token buckets.
    Provides access-driven and background pruning to prevent unbounded memory growth.
    """

    def __init__(
        self,
        capacity: float,
        refill_rate: float,
        ttl_seconds: float = 300.0,
        time_func: Optional[Callable[[], float]] = None,
    ) -> None:
        self.capacity = float(capacity)
        self.refill_rate = float(refill_rate)
        self.ttl_seconds = float(ttl_seconds)
        self.time_func = time_func or time.monotonic
        self._buckets: Dict[str, TokenBucket] = {}
        self._last_accessed: Dict[str, float] = {}
        self._lock: Optional[asyncio.Lock] = None

    def _get_lock(self) -> asyncio.Lock:
        if self._lock is None:
            self._lock = asyncio.Lock()
        return self._lock

    async def consume(
        self, key: str, tokens: float = 1.0, current_time: Optional[float] = None
    ) -> Tuple[bool, float, float, float]:
        """
        Atomically claims tokens for a given client key.

        Returns:
            Tuple[bool, float, float, float]:
                - allowed (bool)
                - remaining (float)
                - retry_after (float)
                - reset_seconds (float)
        """
        now = self.time_func() if current_time is None else current_time
        lock = self._get_lock()
        async with lock:
            self._prune_expired_locked(now)
            if key not in self._buckets:
                self._buckets[key] = TokenBucket(self.capacity, self.refill_rate)

            bucket = self._buckets[key]
            allowed, remaining, retry_after = bucket.consume(tokens=tokens, current_time=now)
            reset_seconds = bucket.reset_time()
            self._last_accessed[key] = now
            return allowed, remaining, retry_after, reset_seconds

    def _prune_expired_locked(self, current_time: float) -> int:
        """
        Evict client buckets that have been inactive longer than the configured TTL.
        Must be called while holding self._lock.
        """
        expired_keys = [
            key
            for key, last_seen in self._last_accessed.items()
            if (current_time - last_seen) > self.ttl_seconds
        ]
        for key in expired_keys:
            self._buckets.pop(key, None)
            self._last_accessed.pop(key, None)
        return len(expired_keys)

    async def prune(self, current_time: Optional[float] = None) -> int:
        """
        Explicit pruning trigger for maintenance tasks or testing.
        """
        now = self.time_func() if current_time is None else current_time
        lock = self._get_lock()
        async with lock:
            return self._prune_expired_locked(now)

    async def size(self) -> int:
        """
        Returns the count of active registered client buckets.
        """
        lock = self._get_lock()
        async with lock:
            return len(self._buckets)


InTokenBucketStore = InMemoryTokenBucketStore
