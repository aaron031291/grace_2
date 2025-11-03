"""
Basic CLI tests
"""

import pytest
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import ConfigManager, CLIConfig


class TestConfig:
    """Test configuration management"""
    
    def test_default_config(self, tmp_path):
        """Test default configuration"""
        config = CLIConfig()
        
        assert config.backend_url == "http://localhost:8000"
        assert config.theme == "dark"
        assert config.auto_login == False
    
    def test_config_save_load(self, tmp_path):
        """Test saving and loading configuration"""
        # Create temporary config directory
        config_dir = tmp_path / ".grace"
        config_file = config_dir / "config.yaml"
        
        # Override config path for testing
        manager = ConfigManager()
        manager.config_dir = config_dir
        manager.config_file = config_file
        
        # Create and save config
        config = CLIConfig(backend_url="http://test:9000", theme="light")
        manager.config = config
        manager.save()
        
        # Load config
        loaded = manager.load()
        
        assert loaded.backend_url == "http://test:9000"
        assert loaded.theme == "light"
    
    def test_config_update(self, tmp_path):
        """Test updating configuration"""
        config_dir = tmp_path / ".grace"
        config_file = config_dir / "config.yaml"
        
        manager = ConfigManager()
        manager.config_dir = config_dir
        manager.config_file = config_file
        
        manager.load()
        manager.update(auto_login=True, theme="light")
        
        assert manager.config.auto_login == True
        assert manager.config.theme == "light"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
