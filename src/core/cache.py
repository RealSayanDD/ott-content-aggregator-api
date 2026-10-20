import json
import logging
from typing import Any

from redis.exceptions import RedisError
from src.core.redis import get_redis
from src.core.config import settings

logger = logging.getLogger(__name__)

DEFAULT_TTL = settings.REDIS_DEFAULT_TTL


async def get_cache(key: str) -> Any | None:
    try:
        redis = get_redis()
        cached_data = await redis.get(key)

        if cached_data is None:
            return None

        return json.loads(cached_data)

    except (RedisError, ValueError, RuntimeError):
        logger.warning(
            "Cache retrieval failed for key: %s",
            key,
            exc_info=True,
        )
        return None


async def set_cache(
    key: str,
    value: Any,
    ttl: int = DEFAULT_TTL,
) -> bool:
    if ttl <= 0:
        raise ValueError("TTL must be greater than zero")

    try:
        redis = get_redis()
        serialized_value = json.dumps(value)
        await redis.set(key, serialized_value, ex=ttl)
        return True

    except (RedisError, TypeError, ValueError, RuntimeError):
        logger.warning(
            "Cache write failed for key: %s",
            key,
            exc_info=True,
        )
        return False


async def delete_cache(key: str) -> bool:
    try:
        redis = get_redis()
        await redis.delete(key)
        return True

    except (RedisError, RuntimeError):
        logger.warning(
            "Cache deletion failed for key: %s",
            key,
            exc_info=True,
        )
        return False
