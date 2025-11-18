"""
Environment Configuration - Phase 0
OFFLINE_MODE and GRACE_PORT flags for CI determinism
"""
import os
from typing import Optional

class GraceEnvironment:
    """Grace environment configuration with CI determinism flags"""
    
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
        return os.getenv("CI", "false").lower() in ("true", "1", "yes") or os.getenv("GITHUB_ACTIONS") == "true"
    
    @staticmethod
    def get_port() -> int:
        """Get Grace port from GRACE_PORT env var or default"""
        try:
            return int(os.getenv("GRACE_PORT", "8000"))
        except ValueError:
            return 8000
    
    @staticmethod
    def should_skip_external_calls() -> bool:
        """Should skip external API calls (offline or CI mode)"""
        return GraceEnvironment.is_offline_mode() or GraceEnvironment.is_ci_mode()
    
    @staticmethod
    def get_config_summary() -> dict:
        """Get current environment configuration"""
        return {
            "offline_mode": GraceEnvironment.is_offline_mode(),
            "dry_run": GraceEnvironment.is_dry_run(),
            "ci_mode": GraceEnvironment.is_ci_mode(),
            "grace_port": GraceEnvironment.get_port(),
            "skip_external_calls": GraceEnvironment.should_skip_external_calls()
        }

# Export for easy imports
OFFLINE_MODE = GraceEnvironment.is_offline_mode()
DRY_RUN = GraceEnvironment.is_dry_run()
CI_MODE = GraceEnvironment.is_ci_mode()
GRACE_PORT = GraceEnvironment.get_port()


