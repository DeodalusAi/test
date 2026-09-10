import time
from concurrent.futures import ThreadPoolExecutor
import pytest
from app.token_bucket import TokenBucket


def test_token_bucket_initialization():
    tb = TokenBucket(rate=10.0, capacity=20.0)
    tokens, capacity, _ = tb.get_state()
    assert tokens == 20.0
    assert capacity == 20.0

    tb_custom = TokenBucket(rate=5.0, capacity=10.0, initial_tokens=3.0)
    tokens, capacity, _ = tb_custom.get_state()
    assert tokens == 3.0
    assert capacity == 10.0


def test_token_bucket_invalid_initialization():
    with pytest.raises(ValueError):
        TokenBucket(rate=0, capacity=10)
    with pytest.raises(ValueError):
        TokenBucket(rate=-1, capacity=10)
    with pytest.raises(ValueError):
        TokenBucket(rate=10, capacity=0)
    with pytest.raises(ValueError):
        TokenBucket(rate=10, capacity=-5)


def test_acquire_tokens():
    tb = TokenBucket(rate=1.0, capacity=5.0)

    allowed, remaining, retry_after = tb.acquire(2.0)
    assert allowed is True
    assert remaining == 3.0
    assert retry_after == 0.0

    allowed, remaining, retry_after = tb.acquire(3.0)
    assert allowed is True
    assert remaining == 0.0
    assert retry_after == 0.0

    allowed, remaining, retry_after = tb.acquire(1.0)
    assert allowed is False
    assert remaining == 0.0
    assert retry_after > 0.0


def test_acquire_invalid_tokens():
    tb = TokenBucket(rate=10.0, capacity=20.0)
    with pytest.raises(ValueError):
        tb.acquire(0)
    with pytest.raises(ValueError):
        tb.acquire(-1)


def test_refill():
    tb = TokenBucket(rate=10.0, capacity=10.0, initial_tokens=0.0)
    time.sleep(0.15)
    allowed, remaining, _ = tb.acquire(1.0)
    assert allowed is True


def test_is_stale():
    tb = TokenBucket(rate=10.0, capacity=10.0)
    now = time.monotonic()
    assert not tb.is_stale(ttl=60.0, now=now)
    assert tb.is_stale(ttl=0.0, now=now + 1.0)


def test_concurrency():
    tb = TokenBucket(rate=100.0, capacity=100.0)

    def worker():
        return tb.acquire(1.0)[0]

    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(lambda _: worker(), range(100)))

    assert sum(results) == 100
