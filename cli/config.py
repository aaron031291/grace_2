"""
Configuration and session management for Grace CLI
"""

import os
import yaml
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict
# keyring is optional; gracefully degrade if unavailable
try:
    import keyring  # type: ignore
except Exception:  # pragma: no cover
    keyring = None


@dataclass
class CLIConfig:
    """CLI configuration"""
    backend_url: str = "http://localhost:8000"
    theme: str = "dark"
    last_workspace: Optional[str] = None
    last_username: Optional[str] = None
    auto_login: bool = False
    websocket_enabled: bool = True
    voice_enabled: bool = True
    
    # UI Settings
    command_palette_key: str = "ctrl+p"
    sidebar_width: int = 30
    chat_history_limit: int = 50
    task_refresh_interval: int = 5
    
    # Audio Settings
    audio_format: str = "wav"
    sample_rate: int = 16000
    channels: int = 1
    
    # Plugin Settings
    plugins_enabled: bool = True
    plugin_dir: Optional[str] = None


class ConfigManager:
    """Manage CLI configuration and credentials"""
    
    def __init__(self):
        self.config_dir = Path.home() / ".grace"
        self.config_file = self.config_dir / "config.yaml"
        self.config: Optional[CLIConfig] = None
        self._ensure_config_dir()
    
    def _ensure_config_dir(self):
        """Ensure config directory exists"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (self.config_dir / "plugins").mkdir(exist_ok=True)
        (self.config_dir / "cache").mkdir(exist_ok=True)
        (self.config_dir / "logs").mkdir(exist_ok=True)
    
    def load(self) -> CLIConfig:
        """Load configuration from file and apply environment overrides"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                data = yaml.safe_load(f) or {}
                self.config = CLIConfig(**data)
        else:
            self.config = CLIConfig()
            self.save()
        # Environment overrides
        backend_env = os.getenv("GRACE_BACKEND_URL")
        if backend_env:
            self.config.backend_url = backend_env
        return self.config
    
    def save(self):
        """Save configuration to file"""
        if self.config:
            with open(self.config_file, 'w') as f:
                yaml.dump(asdict(self.config), f, default_flow_style=False)
    
    def update(self, **kwargs):
        """Update configuration"""
        if not self.config:
            self.load()
        
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
        
        self.save()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        if not self.config:
            self.load()
        return getattr(self.config, key, default)
    
    # Credential Management (using system keyring)
    
    def save_credentials(self, username: str, token: str):
        """Save authentication token securely"""
        try:
            keyring.set_password("grace_cli", username, token)
        except Exception as e:
            print(f"Warning: Could not save credentials securely: {e}")
    
    def get_credentials(self, username: str) -> Optional[str]:
        """Get stored authentication token"""
        try:
            return keyring.get_password("grace_cli", username)
        except Exception:
            return None
    
    def delete_credentials(self, username: str):
        """Delete stored credentials"""
        try:
            keyring.delete_password("grace_cli", username)
        except Exception:
            pass
    
    # Session Management
    
    def save_session(self, username: str, token: str, workspace: Optional[str] = None):
        """Save current session"""
        self.save_credentials(username, token)
        self.update(
            last_username=username,
            last_workspace=workspace or str(Path.cwd())
        )
    
    def restore_session(self) -> Optional[Dict[str, str]]:
        """Restore last session"""
        if not self.config:
            self.load()
        
        if self.config.last_username:
            token = self.get_credentials(self.config.last_username)
            if token:
                return {
                    "username": self.config.last_username,
                    "token": token,
                    "workspace": self.config.last_workspace
                }
        return None
    
    def clear_session(self):
        """Clear current session"""
        if self.config and self.config.last_username:
            self.delete_credentials(self.config.last_username)
        self.update(last_username=None, last_workspace=None)
    
    # Plugin Management
    
    def get_plugin_dir(self) -> Path:
        """Get plugin directory"""
        if not self.config:
            self.load()
        
        if self.config.plugin_dir:
            return Path(self.config.plugin_dir)
        return self.config_dir / "plugins"
    
    def list_plugins(self) -> list:
        """List available plugins"""
        plugin_dir = self.get_plugin_dir()
        if not plugin_dir.exists():
            return []
        
        plugins = []
        for item in plugin_dir.iterdir():
            if item.is_file() and item.suffix == '.py':
                plugins.append(item.stem)
            elif item.is_dir() and (item / "__init__.py").exists():
                plugins.append(item.name)
        return plugins


# Global config instance
_config_manager: Optional[ConfigManager] = None


def get_config() -> ConfigManager:
    """Get global config manager"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager
