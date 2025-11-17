"""
Security Settings
Configuration for authentication and encryption
"""

import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class SecuritySettings(BaseSettings):
    """Security configuration"""
    
    SECRET_KEY: str = os.getenv("SECRET_KEY", "grace-dev-secret-key-change-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    BCRYPT_ROUNDS: int = int(os.getenv("BCRYPT_ROUNDS", "12"))
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"  # Allow extra fields in .env
    )

# Singleton instance
settings = SecuritySettings()
