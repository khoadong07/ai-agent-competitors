from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.backends.inmemory import InMemoryBackend
import json

from pydantic import BaseModel
import os

from app.core.config import settings


async def init_cache():
    """Initialize the shared cache with Redis or in-memory backend."""
    redis_url = settings.REDIS_URL
    if redis_url:
        FastAPICache.init(RedisBackend(redis_url), prefix="app-cache")
    else:
        FastAPICache.init(InMemoryBackend(), prefix="app-cache")

def shared_cache_key(request: BaseModel, endpoint: str) -> str:
    """Generate a cache key based on the request body and endpoint name."""
    request_dict = request.dict()
    return f"{endpoint}:{json.dumps(request_dict, sort_keys=True)}"