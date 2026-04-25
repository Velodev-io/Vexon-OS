from fastapi import HTTPException, Request

try:
    from slowapi import Limiter, _rate_limit_exceeded_handler
    from slowapi.errors import RateLimitExceeded
    from slowapi.util import get_remote_address
except ImportError:
    class Limiter:  # type: ignore[override]
        def __init__(self, *args, **kwargs):
            pass

        def limit(self, *args, **kwargs):
            def decorator(func):
                return func

            return decorator

    def get_remote_address(request: Request) -> str:
        return request.client.host if request.client else "unknown"

    def _rate_limit_exceeded_handler(*args, **kwargs):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    class RateLimitExceeded(Exception):
        pass


limiter = Limiter(key_func=get_remote_address)
