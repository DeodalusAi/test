import math
import threading
import time
from typing import Optional, Tuple


class TokenBucket:
    """Thread-safe Token Bucket implementation using time.monotonic() continuous refill."""

    def __init__(self, rate: float, capacity: float, initial_tokens: Optional[float] = None) -> None:
        if rate <= 0:
            raise ValueError("Refill rate must be strictly positive.")
        if capacity <= 0:
            raise ValueError("Bucket capacity must be strictly positive.")

        self.rate: float = float(rate)
        self.capacity: float = float(capacity)
        self.tokens: float = float(capacity if initial_tokens is None else min(initial_tokens, capacity))
        self.last_refill: float = time.monotonic()
        self.last_accessed: float = self.last_refill
        self._lock: threading.Lock = threading.Lock()

    def _refill(self, now: float) -> None:
        elapsed = now - self.last_refill
        if elapsed > 0:
            new_tokens = elapsed * self.rate
            self.tokens = min(self.capacity, self.tokens + new_tokens)
            self.last_refill = now

    def acquire(self, tokens: float = 1.0) -> Tuple[bool, float, float]:
        """Attempts to consume the specified number of tokens.

        Returns:
            Tuple of (allowed, remaining_tokens, retry_after_seconds).
            - allowed: True if tokens were consumed, False otherwise.
            - remaining_tokens: Remaining tokens in the bucket (floored to int or 0).
            - retry_after_seconds: Seconds required before the next request can succeed (0 if allowed).
        """
        if tokens <= 0:
            raise ValueError("Requested tokens must be strictly positive.")

        with self._lock:
            now = time.monotonic()
            self.last_accessed = now
            self._refill(now)

            if self.tokens >= tokens:
                self.tokens -= tokens
                remaining = max(0.0, self.tokens)
                return True, remaining, 0.0
            else:
                needed = tokens - self.tokens
                retry_after = needed / self.rate
                return False, max(0.0, self.tokens), retry_after

    def get_state(self) -> Tuple[float, float, float]:
        """Returns the current state: (current_tokens, capacity, last_accessed)."""
        with self._lock:
            now = time.monotonic()
            self._refill(now)
            return self.tokens, self.capacity, self.last_accessed

    def is_stale(self, ttl: float, now: Optional[float] = None) -> bool:
        """Checks if bucket is idle beyond ttl and has recovered to full capacity."""
        with self._lock:
            current_time = time.monotonic() if now is None else now
            self._refill(current_time)
            idle = (current_time - self.last_accessed) >= ttl
            full = math.isclose(self.tokens, self.capacity, rel_tol=1e-5, abs_tol=1e-5)
            return idle and full
