from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.core.config import settings
from src.db.session import init_db
from src.api import health, auth, users, titles, genres, platforms


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup (switch to Alembic migrations later)
    await init_db()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "A backend API for discovering movies and TV shows "
        "across streaming platforms."
    ),
    lifespan=lifespan,
)


# Register API routers
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
