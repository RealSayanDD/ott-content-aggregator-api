import json
import logging
import os

from typing import Any

from redis.asyncio import Redis
from redis.exceptions import RedisError


logger = logging.getLogger(__name__)

REDIS_URL = os.getenv(
    "REDIS_URL",
    "redis://localhost:6379/0"
)

# Default cache expiration: 5 minutes
DEFAULT_TTL = 300

# Global Redis connection
redis_client: Redis | None = None


async def init_cache() -> None:
    """
    Initialize the Redis connection.
    """
    global redis_client

    redis_client = Redis.from_url(
        REDIS_URL,
        encoding="utf-8",
        decode_responses=True,
        socket_connect_timeout=2,
        socket_timeout=2,
        health_check_interval=30,
    )

    try:
        await redis_client.ping()
        logger.info("Redis connection established successfully.")

    except RedisError:
        logger.exception(
            "Redis is unavailable. The API will continue without caching."
        )

        await redis_client.aclose()
        redis_client = None


async def close_cache() -> None:
    """
    Close the Redis connection when the application shuts down.
    """
    global redis_client

    if redis_client is not None:
        await redis_client.aclose()
        redis_client = None

        logger.info("Redis connection closed.")


async def get_cache(key: str) -> Any | None:
    """
    Retrieve a cached JSON value.

    Returns None if the key is absent or Redis is unavailable.
    """
    if redis_client is None:
        return None

    try:
        cached_data = await redis_client.get(key)

        if cached_data is None:
            return None

        return json.loads(cached_data)

    except (RedisError, json.JSONDecodeError):
        logger.warning(
            "Unable to retrieve cache key: %s",
            key,
            exc_info=True,
        )

        return None


async def set_cache(
    key: str,
    value: Any,
    ttl: int = DEFAULT_TTL,
) -> bool:
    """
    Store a JSON-serializable value in Redis.

    ttl is the expiration time in seconds.
    """
    if redis_client is None:
        return False

    try:
        serialized_value = json.dumps(value)

        await redis_client.set(
            key,
            serialized_value,
            ex=ttl,
        )

        return True

    except (RedisError, TypeError, ValueError):
        logger.warning(
            "Unable to save cache key: %s",
            key,
            exc_info=True,
        )

        return False


async def delete_cache(key: str) -> bool:
    """
    Delete a specific cache entry.
    """
    if redis_client is None:
        return False

    try:
        await redis_client.delete(key)
        return True

    except RedisError:
        logger.warning(
            "Unable to delete cache key: %s",
            key,
            exc_info=True,
        )

        return False


async def delete_cache_pattern(pattern: str) -> int:
    """
    Delete keys matching a pattern without blocking Redis
    with the KEYS command.

    Example:
        await delete_cache_pattern("titles:*")
    """
    if redis_client is None:
        return 0

    deleted_count = 0

    try:
        async for key in redis_client.scan_iter(
            match=pattern,
            count=100,
        ):
            deleted_count += await redis_client.delete(key)

        return deleted_count

    except RedisError:
        logger.warning(
            "Unable to invalidate cache pattern: %s",
            pattern,
            exc_info=True,
        )

        return deleted_count