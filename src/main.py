
import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from redis.exceptions import RedisError

from src.core.config import settings
from src.core.redis import connect_redis, close_redis
from src.db.session import init_db
from src.api import health, auth, users, titles, genres, platforms, watchlist

# Configure application logging.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Database initialization is essential.
    await init_db()
    logger.info("Database initialized successfully.")

    # Redis is optional.
    app.state.redis_available = False

    try:
        await connect_redis()
        app.state.redis_available = True
        logger.info("Redis connected successfully.")
    except (RedisError, OSError):
        logger.warning(
            "Redis unavailable. Running without caching.",
            exc_info=True,
        )

    try:
        yield
    finally:
        try:
            await close_redis()
            logger.info("Redis connection closed.")
        except (RedisError, OSError):
            logger.warning(
                "Error while closing Redis connection.",
                exc_info=True,
            )


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "A backend API for discovering movies and TV shows "
        "across streaming platforms."
    ),
    lifespan=lifespan,
)

# Configure CORS for your frontend.
# Replace these examples with your actual frontend origins.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Log incoming requests and their processing time.
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.perf_counter()

    try:
        response = await call_next(request)
    except Exception:
        logger.exception(
            "Unhandled error: %s %s",
            request.method,
            request.url.path,
        )
        raise

    duration_ms = (time.perf_counter() - start_time) * 1000

    logger.info(
        "%s %s | Status: %s | Duration: %.2f ms",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )

    response.headers["X-Process-Time"] = f"{duration_ms:.2f}ms"
    return response


# Return a safe response for unexpected server errors.
@app.exception_handler(Exception)
async def global_exception_handler(
    request: Request,
    exc: Exception,
):
    logger.error(
        "Unexpected server error on %s %s",
        request.method,
        request.url.path,
        exc_info=(type(exc), exc, exc.__traceback__),
    )

    return JSONResponse(
        status_code=500,
        content={
            "detail": "An unexpected internal server error occurred."
        },
    )


# Register API routers.
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(titles.router)
app.include_router(genres.router)
app.include_router(platforms.router)
app.include_router(watchlist.router)


@app.get("/", tags=["General"])
async def root():
    return {
        "message": "Welcome to the OTT Content Aggregator API",
        "version": settings.APP_VERSION,
        "documentation": "/docs",
    }
