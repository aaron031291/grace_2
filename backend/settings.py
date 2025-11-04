from functools import lru_cache
from typing import Optional
import os

try:  # Pydantic v2+ separates settings helpers
    from pydantic_settings import BaseSettings  # type: ignore
except ImportError:  # pragma: no cover - fallback for older environments
    from pydantic import BaseSettings  # type: ignore

from pydantic import Field

class Settings(BaseSettings):
    # Core security settings
    SECRET_KEY: str = Field(..., description="JWT signing key; must be strong and kept secret")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(15, ge=5, le=1440, description="Access token expiration in minutes")
    BCRYPT_ROUNDS: int = Field(12, ge=12, le=16, description="bcrypt cost factor")
    RATE_LIMIT_DEFAULT: str = Field("120/minute", description="Default request rate limit applied globally")
    RATE_LIMIT_LOGIN: str = Field("10/minute", description="Rate limit for login attempts per token/IP")
    RATE_LIMIT_REGISTER: str = Field("5/minute", description="Rate limit for account registration attempts")
    SANITIZER_BLOCK_HTML: bool = Field(True, description="Reject HTML markup in request inputs")
    SANITIZER_BLOCK_SQL: bool = Field(True, description="Reject SQL keywords in request inputs")

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
