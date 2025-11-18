"""
Unified Path Management System
Centralizes all path handling for GRACE project
"""

import os
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class GracePaths:
    """
    Centralized path management for GRACE
    All paths flow through here for consistency
    """
    
    def __init__(self, root: Optional[Path] = None):
        """
        Initialize path system
        
        Args:
            root: Project root path (auto-detected if None)
        """
        if root is None:
            # Auto-detect project root
            current = Path(__file__).resolve()
            # Go up from backend/core/paths.py to project root
            self.root = current.parent.parent.parent
        else:
            self.root = Path(root).resolve()
        
        self._validate_root()
        logger.info(f"[PATHS] Project root: {self.root}")
    
    def _validate_root(self):
        """Validate we found the correct project root"""
        required_markers = ['backend', 'pyproject.toml', 'alembic.ini']
        found = sum(1 for marker in required_markers if (self.root / marker).exists())
        
        if found < 2:
            logger.warning(f"[PATHS] Project root validation weak: {self.root}")
    
    # Core directories
    @property
    def backend(self) -> Path:
        """Backend source code directory"""
        return self.root / 'backend'
    
    @property
    def frontend(self) -> Path:
        """Frontend source code directory"""
        return self.root / 'frontend'
    
    @property
    def tests(self) -> Path:
        """Tests directory"""
        return self.root / 'tests'
    
    @property
    def scripts(self) -> Path:
        """Scripts directory"""
        return self.root / 'scripts'
    
    @property
    def docs(self) -> Path:
        """Documentation directory"""
        return self.root / 'docs'
    
    # Data directories
    @property
    def data(self) -> Path:
        """Data directory"""
        path = self.root / 'data'
        path.mkdir(exist_ok=True)
        return path
    
    @property
    def databases(self) -> Path:
        """Databases directory"""
        path = self.root / 'databases'
        path.mkdir(exist_ok=True)
        return path
    
    @property
    def storage(self) -> Path:
        """Storage directory"""
        path = self.root / 'storage'
        path.mkdir(exist_ok=True)
        return path
    
    @property
    def grace_cache(self) -> Path:
        """Grace cache directory"""
        path = self.root / '.grace_cache'
        path.mkdir(exist_ok=True)
        return path
    
    @property
    def grace_vault(self) -> Path:
        """Grace vault directory (secure storage)"""
        path = self.root / '.grace_vault'
        path.mkdir(exist_ok=True)
        return path
    
    @property
    def grace_snapshots(self) -> Path:
        """Grace snapshots directory"""
        path = self.root / '.grace_snapshots'
        path.mkdir(exist_ok=True)
        return path
    
    # Log directories
    @property
    def logs(self) -> Path:
        """Logs directory"""
        path = self.root / 'logs'
        path.mkdir(exist_ok=True)
        return path
    
    # Report directories
    @property
    def reports(self) -> Path:
        """Reports directory"""
        path = self.root / 'reports'
        path.mkdir(exist_ok=True)
        return path
    
    @property
    def exports(self) -> Path:
        """Exports directory"""
        path = self.root / 'exports'
        path.mkdir(exist_ok=True)
        return path
    
    # Configuration files
    @property
    def alembic_ini(self) -> Path:
        """Alembic configuration file"""
        return self.root / 'alembic.ini'
    
    @property
    def pyproject_toml(self) -> Path:
        """Pyproject.toml configuration"""
        return self.root / 'pyproject.toml'
    
    @property
    def env_example(self) -> Path:
        """.env.example file"""
        return self.root / '.env.example'
    
    @property
    def version_file(self) -> Path:
        """VERSION file"""
        return self.root / 'VERSION'
    
    # Database files
    @property
    def main_db(self) -> Path:
        """Main database file"""
        return self.root / 'grace.db'
    
    def get_database(self, name: str) -> Path:
        """Get path to a specific database file"""
        return self.databases / f"{name}.db"
    
    # Knowledge base
    @property
    def knowledge_base(self) -> Path:
        """Knowledge base directory"""
        path = self.root / 'knowledge_base'
        path.mkdir(exist_ok=True)
        return path
    
    # Missions
    @property
    def missions(self) -> Path:
        """Missions directory"""
        path = self.root / 'missions'
        path.mkdir(exist_ok=True)
        return path
    
    # Playbooks
    @property
    def playbooks(self) -> Path:
        """Playbooks directory"""
        path = self.root / 'playbooks'
        path.mkdir(exist_ok=True)
        return path
    
    # Alembic
    @property
    def alembic_versions(self) -> Path:
        """Alembic versions directory"""
        return self.root / 'alembic' / 'versions'
    
    # Helper methods
    def ensure_exists(self, *path_parts: str) -> Path:
        """
        Ensure a path exists, creating it if necessary
        
        Args:
            *path_parts: Path components to join
            
        Returns:
            Resolved path
        """
        path = self.root.joinpath(*path_parts)
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    def relative_to_root(self, path: Path) -> Path:
        """
        Get path relative to project root
        
        Args:
            path: Absolute or relative path
            
        Returns:
            Path relative to root
        """
        try:
            return Path(path).resolve().relative_to(self.root)
        except ValueError:
            # Path is outside root
            return Path(path)
    
    def is_in_project(self, path: Path) -> bool:
        """
        Check if path is within project
        
        Args:
            path: Path to check
            
        Returns:
            True if path is within project root
        """
        try:
            Path(path).resolve().relative_to(self.root)
            return True
        except ValueError:
            return False
    
    def get_config_path(self, config_name: str) -> Path:
        """
        Get path to a configuration file in config/
        
        Args:
            config_name: Configuration file name (with or without .yaml/.json)
            
        Returns:
            Path to configuration file
        """
        config_dir = self.root / 'config'
        config_dir.mkdir(exist_ok=True)
        
        # Try with various extensions
        for ext in ['', '.yaml', '.yml', '.json', '.toml']:
            path = config_dir / f"{config_name}{ext}"
            if path.exists():
                return path
        
        # Return default .yaml path even if doesn't exist
        return config_dir / f"{config_name}.yaml"
    
    def get_report_path(self, report_name: str, extension: str = 'json') -> Path:
        """
        Get path for a report file
        
        Args:
            report_name: Report name
            extension: File extension (default: json)
            
        Returns:
            Path to report file
        """
        if not extension.startswith('.'):
            extension = f'.{extension}'
        return self.reports / f"{report_name}{extension}"
    
    def get_log_path(self, log_name: str) -> Path:
        """
        Get path for a log file
        
        Args:
            log_name: Log name (will append .log if not present)
            
        Returns:
            Path to log file
        """
        if not log_name.endswith('.log'):
            log_name = f"{log_name}.log"
        return self.logs / log_name
    
    def __repr__(self) -> str:
        return f"GracePaths(root={self.root})"


# Global singleton instance
_paths_instance: Optional[GracePaths] = None


def get_paths(root: Optional[Path] = None) -> GracePaths:
    """
    Get global GracePaths instance
    
    Args:
        root: Optional root path (only used on first call)
        
    Returns:
        GracePaths singleton instance
    """
    global _paths_instance
    
    if _paths_instance is None:
        _paths_instance = GracePaths(root=root)
    
    return _paths_instance


# Convenience shortcuts
def get_root() -> Path:
    """Get project root path"""
    return get_paths().root


def get_backend() -> Path:
    """Get backend directory path"""
    return get_paths().backend


def get_data() -> Path:
    """Get data directory path"""
    return get_paths().data


def get_logs() -> Path:
    """Get logs directory path"""
    return get_paths().logs


def get_reports() -> Path:
    """Get reports directory path"""
    return get_paths().reports


# Initialize on import
paths = get_paths()


if __name__ == "__main__":
    # Demo/test
    print("GRACE Unified Path System")
    print("=" * 60)
    print(f"Root: {paths.root}")
    print(f"Backend: {paths.backend}")
    print(f"Frontend: {paths.frontend}")
    print(f"Data: {paths.data}")
    print(f"Logs: {paths.logs}")
    print(f"Reports: {paths.reports}")
    print(f"Database: {paths.main_db}")
    print(f"Vault: {paths.grace_vault}")
    print("=" * 60)
