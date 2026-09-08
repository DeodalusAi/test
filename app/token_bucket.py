import time

class TokenBucket:
    def __init__(self, capacity: int, fill_rate: float, clock=time.monotonic):
        if capacity <= 0 or fill_rate <= 0:
            raise ValueError('capacity and fill_rate must be positive')
        self.capacity = capacity
        self.fill_rate = fill_rate
        self.tokens = float(capacity)
        self.last_update = clock()
        self.clock = clock

    def consume(self, amount: int = 1) -> bool:
        now = self.clock()
        self.tokens = min(self.capacity, self.tokens + (now - self.last_update) * self.fill_rate)
        self.last_update = now
        if self.tokens < amount:
            return False
        self.tokens -= amount
        return True
