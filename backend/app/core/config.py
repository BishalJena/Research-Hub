from pydantic import ConfigDict
from pydantic_settings import BaseSettings
from typing import List, Optional
from functools import lru_cache


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Smart Research Hub"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str
    API_VERSION: str = "v1"

    # Database
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20

    # Redis
    REDIS_URL: str
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str

    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # APCCE Integration
    APCCE_CLIENT_ID: Optional[str] = None
    APCCE_CLIENT_SECRET: Optional[str] = None
    APCCE_API_URL: str = "https://apcce.gov.in/api"
    APCCE_OAUTH_URL: str = "https://apcce.gov.in/oauth"

    # Academic APIs
    SEMANTIC_SCHOLAR_API_KEY: Optional[str] = None
    CROSSREF_EMAIL: str
    OPENALEX_EMAIL: str

    # Vector Database
    PINECONE_API_KEY: Optional[str] = None
    PINECONE_ENVIRONMENT: str = "us-west1-gcp"
    PINECONE_INDEX_NAME: str = "research-hub"

    # AI Models - OpenRouter/OpenAI API
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_API_BASE: str = "https://openrouter.ai/api/v1"
    OPENAI_MODEL: str = "google/gemini-2.5-flash"
    OPENAI_MAX_TOKENS: int = 1500
    OPENAI_TEMPERATURE: float = 0.3
    OPENROUTER_APP_NAME: str = "Smart Research Hub"
    OPENROUTER_APP_URL: str = "https://research-hub.apcce.gov.in"

    # Cohere API - Embeddings
    COHERE_API_KEY: Optional[str] = None
    COHERE_MODEL: str = "embed-english-v3.0"

    # Bhashini API - Translation
    BHASHINI_API_KEY: Optional[str] = None
    BHASHINI_USER_ID: Optional[str] = None
    BHASHINI_API_ENDPOINT: str = "https://api.bhashini.gov.in"

    # API Configuration
    USE_API_MODELS: bool = True
    ENABLE_TRANSLATION: bool = True
    API_BUDGET_ALERT_THRESHOLD: int = 40
    API_BUDGET_HARD_LIMIT: int = 50
    TRACK_API_USAGE: bool = True

    MODEL_CACHE_DIR: str = "/app/models"

    # File Storage
    UPLOAD_DIR: str = "/app/uploads"
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB
    ALLOWED_EXTENSIONS: List[str] = ["pdf", "doc", "docx", "txt"]

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:3001", "http://localhost:8000"]
    CORS_ALLOW_CREDENTIALS: bool = True

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "/app/logs/app.log"

    # Monitoring
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090

    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"  # Allow extra fields from .env without validation errors
    )


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()
