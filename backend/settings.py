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

    # Self-healing feature flags (defaults: observe-only)
    SELF_HEAL_OBSERVE_ONLY: bool = Field(True, description="Enable health state endpoints without executing changes")
    SELF_HEAL_EXECUTE: bool = Field(False, description="Allow automated playbook execution when confident and permitted")
    SELF_HEAL_EXPERIMENTS: bool = Field(False, description="Allow autonomous experiments to close telemetry gaps")
    
    # Self-healing runtime configuration
    SELF_HEAL_RUN_TIMEOUT_MIN: int = Field(10, ge=1, le=60, description="Maximum minutes for a single playbook run (global watchdog)")
    SELF_HEAL_BASE_URL: str = Field("http://localhost:8000", description="Base URL for HTTP health verification checks")
    ENABLE_CLI_VERIFY: bool = Field(False, description="Enable CLI smoke test verification hook (gated, strict timeout)")
    
    # Meta-loop and learning configuration
    META_LOOP_CYCLE_SECONDS: int = Field(120, ge=30, le=600, description="Meta loop coordination cycle interval")
    LEARNING_AGGREGATION_ENABLED: bool = Field(True, description="Enable learning aggregates (24h/7d) endpoint")

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
