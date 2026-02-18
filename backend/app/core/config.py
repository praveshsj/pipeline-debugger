"""
Application configuration using Pydantic settings management.
Loads configuration from environment variables.
"""

from typing import List, Optional
from pydantic import PostgresDsn, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    
    # Application
    APP_NAME: str = "Pipeline Debugger"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # Database
    DATABASE_URL: PostgresDsn
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 0
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # Anthropic Claude
    ANTHROPIC_API_KEY: str
    ANTHROPIC_MODEL: str = "claude-sonnet-4-20250514"
    CLAUDE_API_MAX_RETRIES: int = 3
    CLAUDE_API_TIMEOUT_SECONDS: int = 60
    
    # GitHub
    GITHUB_TOKEN: Optional[str] = None
    GITHUB_ORG: Optional[str] = None
    GITHUB_API_MAX_RETRIES: int = 3
    
    # Airflow (optional - can be configured per user)
    AIRFLOW_BASE_URL: Optional[str] = None
    AIRFLOW_USERNAME: Optional[str] = None
    AIRFLOW_PASSWORD: Optional[str] = None
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 43200  # 30 days
    
    # Feature Flags
    ENABLE_GITHUB_INTEGRATION: bool = True
    ENABLE_AUTO_PR_CREATION: bool = False
    ENABLE_KNOWLEDGE_BASE_LEARNING: bool = True
    
    # Monitoring
    SENTRY_DSN: Optional[str] = None
    POSTHOG_API_KEY: Optional[str] = None
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
