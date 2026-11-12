import logging
from redis.asyncio import Redis
from redis.exceptions import RedisError
from src.core.config import settings

logger = logging.getLogger(__name__)

# Global Redis connection
redis_client: Redis | None = None

#Establishing the Redis
async def connect_redis() -> None:
    
    global redis_client

    # Avoid creating multiple connections.
    if redis_client is not None:
        return

    client = Redis.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True,
        socket_connect_timeout=5,
        socket_timeout=5,
        health_check_interval=30,
    )

    try:
        await client.ping()

        redis_client = client

        logger.info("Redis connection established successfully.")

    except RedisError:
        await client.aclose()

        logger.exception("Failed to connect to Redis.")

        raise

#Closing the Redis connection during application shutdown.
async def close_redis() -> None:

    global redis_client

    if redis_client is not None:
        await redis_client.aclose()
        redis_client = None

        logger.info("Redis connection closed successfully.")

#Return the active Redis client.
def get_redis() -> Redis:
    
    if redis_client is None:
        raise RuntimeError(
            "Redis is not connected. "
            "Call connect_redis() during application startup."
        )

    return redis_client
