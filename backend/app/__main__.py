import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from redis.asyncio import Redis
from sqlalchemy import select
from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed

from app.api.main import api_router
from app.core.config import settings
from app.db import initial_data, session_maker

MAX_TRIES = 60 * 5
WAIT_SECONDS = 5

logger = logging.getLogger(__name__)


@retry(
    stop=stop_after_attempt(MAX_TRIES),
    wait=wait_fixed(WAIT_SECONDS),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARNING),
)
async def check_db_connection() -> None:
    if not settings.db:
        return
    async with session_maker() as session:
        await session.execute(select(1))


@retry(
    stop=stop_after_attempt(MAX_TRIES),
    wait=wait_fixed(WAIT_SECONDS),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARNING),
)
async def check_redis_connection() -> None:
    if not settings.redis:
        return
    redis = Redis(
        host=settings.redis.host,
        port=settings.redis.port,
        db=settings.redis.db,
        username=settings.redis.username,
        password=settings.redis.password,
    )
    await redis.ping()


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.db:
        await check_db_connection()
    if settings.redis:
        await check_redis_connection()
    await initial_data()
    yield


app = FastAPI(
    title=settings.app.name,
    redoc_url=None,
    lifespan=lifespan,
)


app.include_router(api_router, prefix=settings.app.api.v1)


if __name__ == "__main__":
    uvicorn.run(app, host=settings.app.host, port=settings.app.port, log_level=settings.logging)
