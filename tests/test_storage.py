import asyncio
import pytest
from app.storage import InMemoryTokenBucketStore, InTokenBucketStore


def test_alias_equivalence():
    assert InTokenBucketStore is InMemoryTokenBucketStore


def test_consume_allowed_and_denied():
    async def _test():
        store = InMemoryTokenBucketStore(capacity=5.0, refill_rate=1.0)
        allowed, remaining, retry_after, reset_seconds = await store.consume("user1", tokens=3.0)
        assert allowed is True
        assert remaining == 2.0
        assert retry_after == 0.0

        allowed, remaining, retry_after, reset_seconds = await store.consume("user1", tokens=3.0)
        assert allowed is False
        assert remaining == 2.0
        assert retry_after > 0.0

    asyncio.run(_test())


def test_multi_client_isolation():
    async def _test():
        store = InMemoryTokenBucketStore(capacity=5.0, refill_rate=1.0)
        await store.consume("user1", tokens=5.0)
        assert await store.size() == 1

        allowed, remaining, _, _ = await store.consume("user2", tokens=2.0)
        assert allowed is True
        assert remaining == 3.0
        assert await store.size() == 2

    asyncio.run(_test())


def test_ttl_expiration_and_prune():
    async def _test():
        current_time = 1000.0
        store = InMemoryTokenBucketStore(capacity=5.0, refill_rate=1.0, ttl_seconds=60.0)
        await store.consume("user1", tokens=1.0, current_time=current_time)
        await store.consume("user2", tokens=1.0, current_time=current_time + 10.0)
        assert await store.size() == 2

        pruned = await store.prune(current_time=current_time + 65.0)
        assert pruned == 1
        assert await store.size() == 1

        await store.consume("user3", tokens=1.0, current_time=current_time + 80.0)
        assert await store.size() == 1

    asyncio.run(_test())


def test_concurrent_consumption():
    async def _test():
        store = InMemoryTokenBucketStore(capacity=20.0, refill_rate=5.0)
        tasks = [store.consume("concurrent_user", tokens=1.0) for _ in range(10)]
        results = await asyncio.gather(*tasks)
        allowed_count = sum(1 for r in results if r[0] is True)
        assert allowed_count == 10
        assert await store.size() == 1

    asyncio.run(_test())
