"""
Grace Settings - System Configuration
"""

import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # ============ Self-Healing Configuration ============
    SELF_HEAL_OBSERVE_ONLY: bool = False  # CHANGED: Enable execution mode
    SELF_HEAL_EXECUTE: bool = True  # CHANGED: Allow Grace to fix issues
    
    # ============ Snapshot & Rollback ============
    AUTO_SNAPSHOT_BEFORE_ACTION: bool = True  # Snapshot before risky actions
    AUTO_ROLLBACK_ON_ERROR: bool = True  # Rollback immediately on failure
    SNAPSHOT_RETENTION_DAYS: int = 30
    
    # ============ Autonomous Mode ============
    AUTONOMOUS_IMPROVER_ENABLED: bool = True
    AUTONOMOUS_FIX_INTERVAL: int = 300  # 5 minutes
    
    # ============ Learning & Aggregation ============
    LEARNING_AGGREGATION_ENABLED: bool = True
    META_LOOP_ENABLED: bool = True
    
    # ============ Coding Agent ============
    CODING_AGENT_AUTH_BYPASS: bool = True  # CHANGED: Allow system-level access
    CODING_AGENT_ENABLED: bool = True
    
    # ============ Security ============
    REQUIRE_AUTH_FOR_READS: bool = False  # Allow read operations
    REQUIRE_AUTH_FOR_WRITES: bool = False  # CHANGED: Allow Grace full access
    SYSTEM_AUTH_TOKEN: str = "grace_system_internal"  # For internal calls
    
    # ============ Terminal ============
    TERMINAL_ENABLED: bool = True
    TERMINAL_ALLOWED_COMMANDS: list = [
        "grace", "git", "ls", "dir", "cat", "type", "echo",
        "python", "node", "npm", "pip", "curl"
    ]
    TERMINAL_BLOCKED_COMMANDS: list = [
        "rm -rf", "del /f", "format", "shutdown", "reboot"
    ]
    
    # ============ File Upload ============
    CHUNKED_UPLOAD_ENABLED: bool = True
    MAX_CHUNK_SIZE: int = 5 * 1024 * 1024  # 5MB
    MAX_FILE_SIZE: int = 500 * 1024 * 1024  # 500MB
    
    # ============ Logging ============
    STRUCTURED_LOGGING: bool = True
    LOG_LEVEL: str = "INFO"
    
    # ============ Database ============
    DATABASE_URL: str = "sqlite+aiosqlite:///./databases/grace.db"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
