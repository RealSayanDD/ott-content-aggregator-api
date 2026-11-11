from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse
from redis.exceptions import RedisError
from sqlalchemy import text

from src.core.redis import get_redis
from src.db.session import AsyncSessionLocal

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "application": "OTT Content Aggregator API",
    }


@router.get("/ready")
async def readiness_check(request: Request):
    checks = {
        "database": "unavailable",
        "redis": "unavailable",
    }
    database_ready = False

    try:
        async with AsyncSessionLocal() as db:
            await db.execute(text("SELECT 1"))
        checks["database"] = "ok"
        database_ready = True
    except Exception:
        pass

    try:
        await get_redis().ping()
        checks["redis"] = "ok"
    except (RedisError, RuntimeError, OSError):
        checks["redis"] = "disabled"

    code = (
        status.HTTP_200_OK
        if database_ready
        else status.HTTP_503_SERVICE_UNAVAILABLE
    )

    return JSONResponse(
        status_code=code,
        content={
            "status": "ready" if database_ready else "not_ready",
            "checks": checks,
        },
    )