from fastapi import FastAPI
from app.api.routers import sov_insight
from app.core.config import settings

app = FastAPI(
    title="SOV Analysis API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(sov_insight.router)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": settings.APP_VERSION}