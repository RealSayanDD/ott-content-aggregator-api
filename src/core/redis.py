import os

from dotenv import load_dotenv
from redis.asyncio import Redis

load_dotenv()

REDIS_URL = os.getenv(
    "REDIS_URL",
    "redis://localhost:6379/0"
)

REDIS_DEFAULT_TTL = int(
    os.getenv("REDIS_DEFAULT_TTL", "300")
)

redis_client: Redis | None = None


async def connect_redis() -> None:
    global redis_client

    if redis_client is not None:
        return

    client = Redis.from_url(
        REDIS_URL,
        encoding="utf-8",
        decode_responses=True,
        socket_connect_timeout=5,
        socket_timeout=5,
    )

    try:
        await client.ping()
    except Exception:
        await client.aclose()
        raise

    redis_client = client


async def close_redis() -> None:
    global redis_client

    if redis_client is not None:
        await redis_client.aclose()
        redis_client = None


def get_redis() -> Redis:
    if redis_client is None:
        raise RuntimeError(
            "Redis is not connected. "
            "Initialize Redis during application startup."
        )

    return redis_client