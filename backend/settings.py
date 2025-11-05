from functools import lru_cache
from typing import Optional
import os

# Pydantic v2 preferred, with v1 fallback for wider compatibility
try:
    from pydantic_settings import BaseSettings, SettingsConfigDict  # type: ignore
    from pydantic import Field, AnyUrl  # type: ignore
    _PDANTIC_V2 = True
except Exception:  # pragma: no cover - fallback path
    from pydantic import BaseModel, Field  # type: ignore
    BaseSettings = BaseModel  # compatibility shim; does not load env automatically
    AnyUrl = Optional[str]  # lightweight stand-in; not used directly
    _PDANTIC_V2 = False
    class SettingsConfigDict(dict):  # compat shim
        pass

class Settings(BaseSettings):
    # Core security settings
    # Note: Provide a safe dev default to avoid import-time ValidationError during local runs
    SECRET_KEY: str = Field("dev-secret-change-me", description="JWT signing key; must be strong and kept secret")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(15, ge=5, le=1440, description="Access token expiration in minutes")
    BCRYPT_ROUNDS: int = Field(12, ge=12, le=16, description="bcrypt cost factor")

    # Database (not yet wired everywhere; future work)
    DATABASE_URL: Optional[str] = Field(None, description="SQLAlchemy database URL")

    # Pydantic v2 configuration (set only when pydantic-settings is available)
    if _PDANTIC_V2:
        model_config = SettingsConfigDict(
            env_file=os.getenv("GRACE_ENV_FILE", ".env"),
            env_file_encoding="utf-8",
            case_sensitive=True,
        )

    # Pydantic v1 compatibility (ignored by v2)
    if not _PDANTIC_V2:
        class Config:  # type: ignore[override]
            env_file = os.getenv("GRACE_ENV_FILE", ".env")
            env_file_encoding = "utf-8"
            case_sensitive = True

@lru_cache()
def get_settings() -> "Settings":
    return Settings()

# Eager singleton instance for simple imports
settings = get_settings()
