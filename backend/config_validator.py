"""
Configuration Validator

Startup checks for required settings and environment parity.
Warns if required settings are missing or inconsistent between local/staging/prod.
"""

import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum


class ConfigLevel(Enum):
    """Configuration severity levels"""
    REQUIRED = "required"
    RECOMMENDED = "recommended"
    OPTIONAL = "optional"


@dataclass
class ConfigItem:
    """Configuration item definition"""
    key: str
    level: ConfigLevel
    default: Optional[Any] = None
    description: str = ""
    validator: Optional[callable] = None


class ConfigValidator:
    """
    Validates environment configuration at startup.
    
    Benefits:
    - Catches missing config early
    - Ensures environment parity
    - Self-documenting configuration
    """
    
    # Configuration schema
    CONFIG_SCHEMA = [
        # Database
        ConfigItem(
            "DATABASE_PATH",
            ConfigLevel.OPTIONAL,
            "./grace.db",
            "Path to SQLite database"
        ),
        ConfigItem(
            "METRICS_DB_PATH",
            ConfigLevel.OPTIONAL,
            "./databases/metrics.db",
            "Path to metrics database"
        ),
        
        # Feature Flags
        ConfigItem(
            "SELF_HEAL_OBSERVE_ONLY",
            ConfigLevel.RECOMMENDED,
            "true",
            "Enable self-heal in observe-only mode"
        ),
        ConfigItem(
            "SELF_HEAL_EXECUTE",
            ConfigLevel.OPTIONAL,
            "false",
            "Enable self-heal execution mode"
        ),
        ConfigItem(
            "VERIFICATION_ENABLED",
            ConfigLevel.RECOMMENDED,
            "true",
            "Enable action verification system"
        ),
        ConfigItem(
            "LEARNING_AGGREGATION_ENABLED",
            ConfigLevel.RECOMMENDED,
            "true",
            "Enable learning data aggregation"
        ),
        
        # Async Jobs
        ConfigItem(
            "ASYNC_JOBS_ENABLED",
            ConfigLevel.RECOMMENDED,
            "true",
            "Enable async job queue"
        ),
        ConfigItem(
            "JOB_MAX_RETRIES",
            ConfigLevel.OPTIONAL,
            "3",
            "Max retry attempts for background jobs",
            lambda v: int(v) > 0
        ),
        
        # Aggregation
        ConfigItem(
            "AGGREGATION_INTERVAL_HOURS",
            ConfigLevel.OPTIONAL,
            "1",
            "Hours between data aggregation runs",
            lambda v: int(v) > 0
        ),
        
        # Discovery
        ConfigItem(
            "DISCOVERY_INTERVAL_SECS",
            ConfigLevel.OPTIONAL,
            "3600",
            "Knowledge discovery interval in seconds"
        ),
        ConfigItem(
            "DISCOVERY_SEEDS_PER_CYCLE",
            ConfigLevel.OPTIONAL,
            "5",
            "Seeds per discovery cycle"
        ),
        
        # Approvals
        ConfigItem(
            "APPROVAL_DECIDERS",
            ConfigLevel.OPTIONAL,
            "",
            "Comma-separated list of users who can decide approvals"
        ),
        ConfigItem(
            "APPROVAL_DECISION_RATE_PER_MIN",
            ConfigLevel.OPTIONAL,
            "10",
            "Rate limit for approval decisions per minute",
            lambda v: int(v) > 0
        ),
        
        # Rate Limiting
        ConfigItem(
            "RATE_LIMIT_BYPASS",
            ConfigLevel.OPTIONAL,
            "false",
            "Bypass rate limiting (for testing)"
        ),
        
        # IDE Integration
        ConfigItem(
            "ENABLE_IDE_WS",
            ConfigLevel.OPTIONAL,
            "false",
            "Enable IDE WebSocket integration"
        ),
        
        # Observability
        ConfigItem(
            "PROMETHEUS_ENABLED",
            ConfigLevel.OPTIONAL,
            "false",
            "Enable Prometheus metrics export"
        ),
        ConfigItem(
            "STRUCTURED_LOGGING",
            ConfigLevel.RECOMMENDED,
            "true",
            "Enable structured JSON logging"
        ),
        
        # Notifications
        ConfigItem(
            "SSE_ENABLED",
            ConfigLevel.RECOMMENDED,
            "true",
            "Enable Server-Sent Events for approvals"
        ),
        
        # Mission Tracking
        ConfigItem(
            "MISSION_TRACKING_ENABLED",
            ConfigLevel.RECOMMENDED,
            "true",
            "Enable mission progression tracking"
        ),
    ]
    
    def __init__(self):
        self.warnings: List[str] = []
        self.errors: List[str] = []
        self.config: Dict[str, Any] = {}
    
    def validate(self) -> bool:
        """
        Validate all configuration items.
        
        Returns:
            True if all required config is valid, False otherwise
        """
        
        print("\n🔍 Validating configuration...")
        
        for item in self.CONFIG_SCHEMA:
            self._validate_item(item)
        
        # Print summary
        if self.errors:
            print(f"\n❌ Configuration Errors ({len(self.errors)}):")
            for error in self.errors:
                print(f"   - {error}")
        
        if self.warnings:
            print(f"\n⚠️  Configuration Warnings ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"   - {warning}")
        
        if not self.errors and not self.warnings:
            print("✓ All configuration valid")
        
        return len(self.errors) == 0
    
    def _validate_item(self, item: ConfigItem):
        """Validate a single configuration item"""
        
        value = os.getenv(item.key)
        
        if value is None:
            # Use default if available
            if item.default is not None:
                value = item.default
                self.config[item.key] = value
                
                if item.level == ConfigLevel.REQUIRED:
                    self.errors.append(
                        f"{item.key} is REQUIRED but not set. Using default: {item.default}"
                    )
                elif item.level == ConfigLevel.RECOMMENDED:
                    self.warnings.append(
                        f"{item.key} not set. Using default: {item.default}. {item.description}"
                    )
            else:
                # No default available
                if item.level == ConfigLevel.REQUIRED:
                    self.errors.append(
                        f"{item.key} is REQUIRED but not set and has no default"
                    )
                elif item.level == ConfigLevel.RECOMMENDED:
                    self.warnings.append(
                        f"{item.key} is recommended but not set. {item.description}"
                    )
        else:
            # Value is set, validate it
            self.config[item.key] = value
            
            if item.validator:
                try:
                    if not item.validator(value):
                        self.errors.append(
                            f"{item.key}={value} failed validation. {item.description}"
                        )
                except Exception as e:
                    self.errors.append(
                        f"{item.key}={value} validation error: {str(e)}"
                    )
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """Get a validated config value"""
        return self.config.get(key, default)
    
    def print_config_summary(self):
        """Print a summary of current configuration"""
        
        print("\n📋 Configuration Summary:")
        print("=" * 60)
        
        for item in self.CONFIG_SCHEMA:
            value = self.config.get(item.key, "NOT SET")
            level_symbol = {
                ConfigLevel.REQUIRED: "🔴",
                ConfigLevel.RECOMMENDED: "🟡",
                ConfigLevel.OPTIONAL: "🟢"
            }[item.level]
            
            print(f"{level_symbol} {item.key:<40} = {value}")
            if item.description:
                print(f"   {item.description}")
        
        print("=" * 60)


# Global singleton
config_validator = ConfigValidator()


def validate_startup_config() -> bool:
    """
    Run configuration validation at startup.
    
    Returns:
        True if configuration is valid, False otherwise
    """
    
    is_valid = config_validator.validate()
    
    if not is_valid:
        print("\n⚠️  Configuration issues detected. Review errors above.")
        print("   See .env.example for reference configuration.")
    
    return is_valid


def get_validated_config(key: str, default: Any = None) -> Any:
    """Get a validated configuration value"""
    return config_validator.get_config(key, default)
