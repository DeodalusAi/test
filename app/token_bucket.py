import asyncio
import math
import time
from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class BucketState:
    tokens: float
    capacity: float
    refill_rate: float
    last_updated: float


@dataclass(frozen=True)
class ConsumptionResult:
    allowed: bool
    limit: int
    remaining: int
    retry_after: float
    reset_in: float


class TokenBucketManager:
    """Manages token buckets for multiple keys in memory with asyncio concurrency protection."""

    def __init__(self, default_rate: float = 5.0, default_capacity: float = 10.0) -> None:
        if default_rate <= 0:
            raise ValueError("default_rate must be positive")
        if default_capacity <= 0:
            raise ValueError("default_capacity must be positive")
        self.default_rate = default_rate
        self.default_capacity = default_capacity
        self._buckets: Dict[str, BucketState] = {}
        self._lock: Optional[asyncio.Lock] = None

    def _get_lock(self) -> asyncio.Lock:
        if self._lock is None:
            self._lock = asyncio.Lock()
        return self._lock

    def _replenish(self, bucket: BucketState, current_time: float) -> None:
        elapsed = max(0.0, current_time - bucket.last_updated)
        bucket.tokens = min(bucket.capacity, bucket.tokens + (elapsed * bucket.refill_rate))
        bucket.last_updated = current_time

    async def consume(
        self,
        key: str,
        cost: float = 1.0,
        rate: Optional[float] = None,
        capacity: Optional[float] = None,
        current_time: Optional[float] = None,
    ) -> ConsumptionResult:
        if cost <= 0:
            raise ValueError("cost must be greater than zero")
        if rate is not None and rate <= 0:
            raise ValueError("rate must be positive")
        if capacity is not None and capacity <= 0:
            raise ValueError("capacity must be positive")

        now = time.monotonic() if current_time is None else current_time
        bucket_rate = self.default_rate if rate is None else rate
        bucket_cap = self.default_capacity if capacity is None else capacity

        async with self._get_lock():
            if key not in self._buckets:
                self._buckets[key] = BucketState(
                    tokens=bucket_cap,
                    capacity=bucket_cap,
                    refill_rate=bucket_rate,
                    last_updated=now,
                )
            else:
                bucket = self._buckets[key]
                self._replenish(bucket, now)
                if rate is not None:
                    bucket.refill_rate = rate
                if capacity is not None:
                    bucket.capacity = capacity
                    bucket.tokens = min(bucket.tokens, capacity)

            bucket = self._buckets[key]
            self._replenish(bucket, now)

            limit = int(bucket.capacity)
            if bucket.tokens >= cost:
                bucket.tokens -= cost
                remaining = int(math.floor(bucket.tokens))
                needed_for_full = max(0.0, bucket.capacity - bucket.tokens)
                reset_in = needed_for_full / bucket.refill_rate if bucket.refill_rate > 0 else 0.0
                return ConsumptionResult(
                    allowed=True,
                    limit=limit,
                    remaining=remaining,
                    retry_after=0.0,
                    reset_in=reset_in,
                )
            else:
                needed = cost - bucket.tokens
                retry_after = needed / bucket.refill_rate if bucket.refill_rate > 0 else float("inf")
                remaining = int(math.floor(max(0.0, bucket.tokens)))
                needed_for_full = max(0.0, bucket.capacity - bucket.tokens)
                reset_in = needed_for_full / bucket.refill_rate if bucket.refill_rate > 0 else 0.0
                return ConsumptionResult(
                    allowed=False,
                    limit=limit,
                    remaining=remaining,
                    retry_after=retry_after,
                    reset_in=reset_in,
                )

    async def reset(self, key: Optional[str] = None) -> None:
        async with self._get_lock():
            if key is None:
                self._buckets.clear()
            else:
                self._buckets.pop(key, None)
