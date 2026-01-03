"""
Configuration settings for the API Gateway
"""
from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    """Application settings."""
    
    # API Settings
    API_TITLE: str = "Secure API Gateway"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "Production-ready API Gateway with comprehensive security features"
    
    # Security Settings
    SECRET_KEY: str = "your-secret-key-change-this-in-production-make-it-very-long-and-random"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100  # requests per window
    RATE_LIMIT_WINDOW: int = 60     # window in seconds
    
    # Redis Settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # CORS Settings
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Database
    DATABASE_URL: str = "sqlite:///./api_gateway.db"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/api_gateway.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()