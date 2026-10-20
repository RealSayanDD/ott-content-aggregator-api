
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from redis.exceptions import RedisError

from src.core.config import settings
from src.core.redis import connect_redis, close_redis
from src.db.session import init_db
from src.api import health, auth, users, titles, genres, platforms

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize the database.
    await init_db()

    # Redis is optional: the API can run without caching.
    try:
        await connect_redis()
    except (RedisError, OSError):
        logger.warning(
            "Redis is unavailable. Continuing without caching.",
            exc_info=True,
        )

    try:
        yield
    finally:
        await close_redis()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "A backend API for discovering movies and TV shows "
        "across streaming platforms."
    ),
    lifespan=lifespan,
)

# Register API routers.
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(titles.router)
app.include_router(genres.router)
app.include_router(platforms.router)


@app.get("/")
async def root():
    return {
        "message": "Welcome to the OTT Content Aggregator API",
        "version": settings.APP_VERSION,
        "documentation": "/docs",
    }
