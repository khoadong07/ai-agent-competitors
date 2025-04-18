import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    APP_VERSION: str = "1.0.0"
    GATEWAY_URL: str = os.getenv("GATEWAY_URL", "")
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    CMS_GATEWAY_URL: str = "https://cms-gateway.radaa.net/kompaql"
    REDIS_URL: str = os.getenv("REDIS_URL", "")
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()