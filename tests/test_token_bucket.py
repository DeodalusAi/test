import asyncio
import pytest
from app.token_bucket import TokenBucketManager


def test_init_validation():
    manager = TokenBucketManager(default_rate=5.0, default_capacity=10.0)
    assert manager.default_rate == 5.0
    assert manager.default_capacity == 10.0

    with pytest.raises(ValueError):
        TokenBucketManager(default_rate=0)

    with pytest.raises(ValueError):
        TokenBucketManager(default_rate=-1)

    with pytest.raises(ValueError):
        TokenBucketManager(default_capacity=0)

    with pytest.raises(ValueError):
        TokenBucketManager(default_capacity=-5)


def test_consume_success():
    async def run():
        manager = TokenBucketManager(default_rate=2.0, default_capacity=5.0)
        result = await manager.consume("user1", cost=2.0, current_time=100.0)
        assert result.allowed is True
        assert result.limit == 5
        assert result.remaining == 3
        assert result.retry_after == 0.0
        assert result.reset_in == 1.0

    asyncio.run(run())


def test_consume_rate_limit_exceeded():
    async def run():
        manager = TokenBucketManager(default_rate=2.0, default_capacity=5.0)
        res1 = await manager.consume("user1", cost=4.0, current_time=100.0)
        assert res1.allowed is True
        assert res1.remaining == 1

        res2 = await manager.consume("user1", cost=3.0, current_time=100.0)
        assert res2.allowed is False
        assert res2.limit == 5
        assert res2.remaining == 1
        assert pytest.approx(res2.retry_after) == 1.0
        assert pytest.approx(res2.reset_in) == 2.0

    asyncio.run(run())


def test_replenish_over_time():
    async def run():
        manager = TokenBucketManager(default_rate=2.0, default_capacity=10.0)
        await manager.consume("user1", cost=8.0, current_time=100.0)

        # After 2 seconds, 4 tokens should be replenished (2.0 + 4.0 = 6.0 tokens remaining)
        result = await manager.consume("user1", cost=5.0, current_time=102.0)
        assert result.allowed is True
        assert result.remaining == 1

    asyncio.run(run())


def test_invalid_parameters():
    async def run():
        manager = TokenBucketManager()
        with pytest.raises(ValueError):
            await manager.consume("user1", cost=0)
        with pytest.raises(ValueError):
            await manager.consume("user1", cost=-1)
        with pytest.raises(ValueError):
            await manager.consume("user1", cost=1, rate=0)
        with pytest.raises(ValueError):
            await manager.consume("user1", cost=1, capacity=0)

    asyncio.run(run())


def test_reset():
    async def run():
        manager = TokenBucketManager(default_rate=1.0, default_capacity=5.0)
        await manager.consume("u1", cost=5.0, current_time=10.0)
        await manager.consume("u2", cost=5.0, current_time=10.0)

        # Reset single key
        await manager.reset("u1")
        res_u1 = await manager.consume("u1", cost=5.0, current_time=10.0)
        assert res_u1.allowed is True

        res_u2 = await manager.consume("u2", cost=1.0, current_time=10.0)
        assert res_u2.allowed is False

        # Reset all keys
        await manager.reset()
        res_u2_after = await manager.consume("u2", cost=5.0, current_time=10.0)
        assert res_u2_after.allowed is True

    asyncio.run(run())


def test_concurrent_consumption():
    async def run():
        manager = TokenBucketManager(default_rate=1.0, default_capacity=10.0)
        tasks = [manager.consume("shared_user", cost=1.0, current_time=10.0) for _ in range(12)]
        results = await asyncio.gather(*tasks)

        allowed_count = sum(1 for r in results if r.allowed)
        rejected_count = sum(1 for r in results if not r.allowed)

        assert allowed_count == 10
        assert rejected_count == 2

    asyncio.run(run())
