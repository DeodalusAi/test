from app.token_bucket import TokenBucket

def test_token_bucket_refills_from_elapsed_time():
    now = [0.0]
    bucket = TokenBucket(1, 1.0, clock=lambda: now[0])
    assert bucket.consume()
    assert not bucket.consume()
    now[0] = 1.0
    assert bucket.consume()

def test_token_bucket_rejects_invalid_configuration():
    try:
        TokenBucket(0, 1.0)
    except ValueError:
        pass
    else:
        raise AssertionError('invalid capacity was accepted')
