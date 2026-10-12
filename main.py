from fastapi import FastAPI

app = FastAPI(
    title="OTT Content Aggregator API",
    description="An API for discovering movies and streaming platforms.",
    version="1.0.0",
)


@app.get("/")
async def root():
    return {
        "message": "OTT Content Aggregator API is running"
    }