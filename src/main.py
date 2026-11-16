from src.api.routes.genres import router as genres_router
from src.api.routes.platforms import router as platforms_router
from fastapi import FastAPI

from src.api.routes.titles import router as titles_router

app = FastAPI(
    title="OTT Content Aggregator API",
    description="API for managing movies, shows and streaming platforms",
    version="1.0.0"
)

app.include_router(titles_router)
app.include_router(genres_router)
app.include_router(platforms_router)

@app.get("/")
async def home():
    return {
        "message": "OTT Content Aggregator API is running successfully!"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy"
    }
