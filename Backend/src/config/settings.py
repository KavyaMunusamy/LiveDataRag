import os
from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    # API Settings
    PROJECT_NAME: str = "Live Data RAG with Actions"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Database & Vector Store
    PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY", "")
    PINECONE_ENVIRONMENT: str = os.getenv("PINECONE_ENVIRONMENT", "us-west1-gcp")
    PINECONE_INDEX: str = "live-rag-index"
    
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    POSTGRES_URL: str = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/live_rag")
    
    # LLM Settings
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    LLM_MODEL: str = "gpt-4-turbo-preview"  # or "claude-3-opus-20240229"
    
    # Data Sources
    FINANCIAL_API_KEY: str = os.getenv("ALPHA_VANTAGE_KEY", "")
    NEWS_API_KEY: str = os.getenv("NEWSAPI_KEY", "")
    
    # Action Safety
    MAX_AUTONOMOUS_ACTIONS_PER_HOUR: int = 50
    REQUIRED_CONFIRMATION_FOR: List[str] = ["financial_trade", "user_delete", "system_shutdown"]
    
    # Monitoring
    SENTRY_DSN: Optional[str] = os.getenv("SENTRY_DSN")
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields from .env

settings = Settings()