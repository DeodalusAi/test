from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from app.token_bucket import TokenBucket

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, capacity=10, fill_rate=1.0):
        super().__init__(app)
        self.bucket = TokenBucket(capacity, fill_rate)

    async def dispatch(self, request, call_next):
        if not self.bucket.consume():
            return JSONResponse({'detail': 'Rate limit exceeded'}, status_code=429, headers={'Retry-After': '1'})
        return await call_next(request)
