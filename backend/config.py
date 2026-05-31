import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://mongodb:27017")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "smart_classroom")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    AI_SERVICE_URL: str = os.getenv("AI_SERVICE_URL", "http://ai-service:8001")
    PORT: int = 8000

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
