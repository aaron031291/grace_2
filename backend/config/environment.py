"""
Environment Configuration
Centralized environment variable management for Grace
"""

import os
from typing import Optional

class GraceEnvironment:
    """Environment configuration for Grace"""
    
    @staticmethod
    def get_port() -> int:
        """Get Grace API port from environment or default"""
        return int(os.getenv("GRACE_PORT", "8000"))
    
    @staticmethod
    def is_offline_mode() -> bool:
        """Check if running in offline mode (no external calls)"""
        return os.getenv("OFFLINE_MODE", "false").lower() in ("true", "1", "yes")
    
    @staticmethod
    def is_dry_run() -> bool:
        """Check if running in dry-run mode (boot only, no services)"""
        return os.getenv("DRY_RUN", "false").lower() in ("true", "1", "yes")
    
    @staticmethod
    def is_ci_mode() -> bool:
        """Check if running in CI environment"""
        return os.getenv("CI", "false").lower() in ("true", "1", "yes")
    
    @staticmethod
    def get_log_level() -> str:
        """Get logging level from environment"""
        return os.getenv("LOG_LEVEL", "INFO").upper()
    
    @staticmethod
    def get_db_path() -> str:
        """Get database path from environment or default"""
        return os.getenv("GRACE_DB_PATH", "databases/grace.db")
    
    @staticmethod
    def get_environment() -> str:
        """Get current environment (dev/staging/prod)"""
        return os.getenv("GRACE_ENV", "development")
    
    @staticmethod
    def should_skip_external_calls() -> bool:
        """Should skip external API calls (web search, LLM, etc.)"""
        return GraceEnvironment.is_offline_mode() or GraceEnvironment.is_ci_mode()


# Convenience exports
GRACE_PORT = GraceEnvironment.get_port()
OFFLINE_MODE = GraceEnvironment.is_offline_mode()
DRY_RUN = GraceEnvironment.is_dry_run()
CI_MODE = GraceEnvironment.is_ci_mode()
LOG_LEVEL = GraceEnvironment.get_log_level()
GRACE_ENV = GraceEnvironment.get_environment()

__all__ = [
    'GraceEnvironment',
    'GRACE_PORT',
    'OFFLINE_MODE',
    'DRY_RUN',
    'CI_MODE',
    'LOG_LEVEL',
    'GRACE_ENV',
]
