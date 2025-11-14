"""
Grace Settings - System Configuration
Merged: Pydantic v2/v1 fallback + external integrations + autonomous mode flags
"""

from functools import lru_cache
from typing import Optional
import os

# Pydantic v2 preferred, with v1 fallback for wider compatibility
try:
    from pydantic_settings import BaseSettings, SettingsConfigDict  # type: ignore
    from pydantic import Field, AnyUrl, SecretStr  # type: ignore
    _PDANTIC_V2 = True
except Exception:  # pragma: no cover - fallback path
    from pydantic import BaseModel, Field  # type: ignore
    BaseSettings = BaseModel  # compatibility shim; does not load env automatically
    AnyUrl = Optional[str]  # lightweight stand-in; not used directly
    SecretStr = Optional[str]  # type: ignore
    _PDANTIC_V2 = False
    class SettingsConfigDict(dict):  # compat shim
        pass


class Settings(BaseSettings):
    # ============ Core Security Settings ============
    SECRET_KEY: str = Field("dev-secret-change-me", description="JWT signing key; must be strong and kept secret")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(15, ge=5, le=1440, description="Access token expiration in minutes")
    BCRYPT_ROUNDS: int = Field(12, ge=12, le=16, description="bcrypt cost factor")
    
    # ============ Security Authorization ============
    REQUIRE_AUTH_FOR_READS: bool = Field(False, description="Allow read operations")
    REQUIRE_AUTH_FOR_WRITES: bool = Field(False, description="Allow Grace full access")
    SYSTEM_AUTH_TOKEN: str = Field("grace_system_internal", description="For internal calls")

    # ============ Database ============
    DATABASE_URL: str = Field("sqlite+aiosqlite:///./databases/grace.db", description="SQLAlchemy database URL")

    # ============ External Integrations / Secrets ============
    AMP_API_KEY: Optional[SecretStr] = Field(None, description="AMP API key for external integration")  # type: ignore[valid-type]
    GITHUB_TOKEN: Optional[SecretStr] = Field(None, description="GitHub token for API access")  # type: ignore[valid-type]
    
    # ============ Self-Healing Configuration ============
    SELF_HEAL_OBSERVE_ONLY: bool = Field(False, description="Enable execution mode")
    SELF_HEAL_EXECUTE: bool = Field(True, description="Allow automated playbook execution")
    SELF_HEAL_EXPERIMENTS: bool = Field(False, description="Allow autonomous experiments to close telemetry gaps")
    ENABLE_CLI_VERIFY: bool = Field(False, description="Enable optional CLI smoke verification hook in runner")
    SELF_HEAL_BASE_URL: str = Field("http://localhost:8000", description="Base URL used by self-heal verifications")
    SELF_HEAL_RUN_TIMEOUT_MIN: int = Field(10, ge=1, le=120, description="Global timeout (minutes) for a playbook run")
    
    # ============ Snapshot & Rollback ============
    AUTO_SNAPSHOT_BEFORE_ACTION: bool = Field(True, description="Snapshot before risky actions")
    AUTO_ROLLBACK_ON_ERROR: bool = Field(True, description="Rollback immediately on failure")
    SNAPSHOT_RETENTION_DAYS: int = Field(30, description="Days to retain snapshots")
    
    # ============ Autonomous Mode ============
    AUTONOMOUS_IMPROVER_ENABLED: bool = Field(True, description="Enable autonomous improver loop")
    AUTONOMOUS_FIX_INTERVAL: int = Field(300, description="5 minutes between autonomous fixes")
    
    # ============ Learning & Aggregation ============
    LEARNING_AGGREGATION_ENABLED: bool = Field(True, description="Enable learning aggregation")
    META_LOOP_ENABLED: bool = Field(True, description="Enable meta-loop reflection")
    
    # ============ Coding Agent ============
    CODING_AGENT_AUTH_BYPASS: bool = Field(True, description="Allow system-level access")
    CODING_AGENT_ENABLED: bool = Field(True, description="Enable coding agent")
    
    # ============ Terminal ============
    TERMINAL_ENABLED: bool = Field(True, description="Enable terminal commands")
    TERMINAL_ALLOWED_COMMANDS: list = Field(
        default_factory=lambda: ["grace", "git", "ls", "dir", "cat", "type", "echo", "python", "node", "npm", "pip", "curl"],
        description="Allowed terminal commands"
    )
    TERMINAL_BLOCKED_COMMANDS: list = Field(
        default_factory=lambda: ["rm -rf", "del /f", "format", "shutdown", "reboot"],
        description="Blocked terminal commands"
    )
    
    # ============ File Upload ============
    CHUNKED_UPLOAD_ENABLED: bool = Field(True, description="Enable chunked uploads")
    MAX_CHUNK_SIZE: int = Field(5 * 1024 * 1024, description="5MB max chunk size")
    MAX_FILE_SIZE: int = Field(500 * 1024 * 1024, description="500MB max file size")
    
    # ============ Logging ============
    STRUCTURED_LOGGING: bool = Field(True, description="Enable structured logging")
    LOG_LEVEL: str = Field("INFO", description="Logging level")

    # Pydantic v2 configuration (set only when pydantic-settings is available)
    if _PDANTIC_V2:
        model_config = SettingsConfigDict(
            env_file=os.getenv("GRACE_ENV_FILE", ".env"),
            env_file_encoding="utf-8",
            case_sensitive=True,
            extra="allow",
        )

    # Pydantic v1 compatibility (ignored by v2)
    if not _PDANTIC_V2:
        class Config:  # type: ignore[override]
            env_file = os.getenv("GRACE_ENV_FILE", ".env")
            env_file_encoding = "utf-8"
            case_sensitive = True
            extra = "allow"


@lru_cache()
def get_settings() -> "Settings":
    return Settings()


# Eager singleton instance for simple imports
settings = get_settings()
