from functools import lru_cache
from pydantic import BaseSettings, Field, AnyUrl
from typing import Optional
import os

class Settings(BaseSettings):
    # Core security settings
    SECRET_KEY: str = Field(..., description="JWT signing key; must be strong and kept secret")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(15, ge=5, le=1440, description="Access token expiration in minutes")
    BCRYPT_ROUNDS: int = Field(12, ge=12, le=16, description="bcrypt cost factor")

    # Database (not yet wired everywhere; future work)
    DATABASE_URL: Optional[str] = Field(None, description="SQLAlchemy database URL")

    class Config:
        env_file = os.getenv("GRACE_ENV_FILE", ".env")
        env_file_encoding = "utf-8"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]

# Eager singleton instance for simple imports
settings = get_settings()
