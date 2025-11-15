"""
Agentic Configuration Loader

Loads configuration for all agentic systems from YAML config file
and environment variables.
"""

import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path


class AgenticConfig:
    """Configuration for agentic systems"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or os.getenv(
            "AGENTIC_CONFIG_PATH",
            "config/agentic_config.yaml"
        )
        self.config: Dict[str, Any] = {}
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file"""
        
        config_file = Path(self.config_path)
        
        if config_file.exists():
            with open(config_file, 'r') as f:
                self.config = yaml.safe_load(f) or {}
            print(f"[OK] Loaded agentic config from {self.config_path}")
        else:
            print(f"[WARN]  Agentic config not found at {self.config_path}, using defaults")
            self.config = self._default_config()
    
    def _default_config(self) -> Dict[str, Any]:
        """Default configuration"""
        return {
            "proactive_intelligence": {"enabled": True, "prediction_interval_seconds": 180},
            "autonomous_planner": {"enabled": True, "max_concurrent_recoveries": 10},
            "learning": {"enabled": True, "learning_cycle_hours": 1},
            "human_collaboration": {"enabled": True},
            "resource_stewardship": {"enabled": True},
            "ethics_sentinel": {"enabled": True},
            "meta_loop": {"enabled": True, "cycle_interval_seconds": 300},
            "sharding": {"enabled": False},
            "observability": {"enabled": True, "verbosity": "summary"}
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get config value"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        
        return value if value is not None else default
    
    def is_enabled(self, system: str) -> bool:
        """Check if system is enabled"""
        return self.get(f"{system}.enabled", True)


agentic_config = AgenticConfig()
