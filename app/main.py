from fastapi import FastAPI
from app.api.routers import sov_insight, sentiment_breakdown_insight, brand_health, channel_breakdown, brand_attribute_by_sentiment, mention_trendlines
from app.core.config import settings
from app.services.sb_api_service import APISentimentAggregationService

app = FastAPI(
    title="SOV Analysis API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(sov_insight.router)
app.include_router(sentiment_breakdown_insight.router)
app.include_router(brand_health.router)
app.include_router(channel_breakdown.router)
app.include_router(brand_attribute_by_sentiment.router)
app.include_router(mention_trendlines.router)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": settings.APP_VERSION}

