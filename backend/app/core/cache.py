from cashews import Cache

from app.core.config import settings

cache = Cache()

if settings.redis:
    cache.setup(
        f"redis://{settings.redis.host}:{settings.redis.port}",
        username=settings.redis.username,
        password=settings.redis.password,
    )
else:
    # TODO: To settings.
    cache.setup("mem://?size=500")
