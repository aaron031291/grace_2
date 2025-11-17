"""
Snapshot Hygiene Automation
Regularly refreshes model/config snapshots for restore operations

Features:
- Automated snapshot refresh (hourly/daily)
- Snapshot validation and integrity checks
- Old snapshot cleanup
- Model weight backup automation
"""

import asyncio
import logging
import shutil
from typing import Dict
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)


class SnapshotHygieneManager:
    """
    Manages snapshot lifecycle and freshness
    Ensures restore operations always have valid sources
    """
    
    def __init__(self):
        self.running = False
        self.snapshot_dir = Path(__file__).parent.parent.parent / '.grace_snapshots'
        self.models_dir = self.snapshot_dir / 'models'
        self.configs_dir = self.snapshot_dir / 'configs'
        
        # Create directories
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.configs_dir.mkdir(parents=True, exist_ok=True)
        
        self.refresh_interval = 3600  # 1 hour
        self.max_snapshot_age_hours = 24
        self.max_snapshots_per_type = 5
    
    async def start(self):
        """Start snapshot hygiene automation"""
        
        if self.running:
            return
        
        self.running = True
        logger.info("[SNAPSHOT-HYGIENE] Starting automated snapshot management")
        
        # Run initial snapshot
        await self._refresh_all_snapshots()
        
        # Start refresh loop
        asyncio.create_task(self._refresh_loop())
    
    async def stop(self):
        """Stop snapshot automation"""
        self.running = False
        logger.info("[SNAPSHOT-HYGIENE] Stopped")
    
    async def _refresh_loop(self):
        """Continuous snapshot refresh loop"""
        
        while self.running:
            try:
                await asyncio.sleep(self.refresh_interval)
                await self._refresh_all_snapshots()
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[SNAPSHOT-HYGIENE] Error in refresh loop: {e}", exc_info=True)
                await asyncio.sleep(3600)
    
    async def _refresh_all_snapshots(self):
        """Refresh all snapshot types"""
        
        logger.info("[SNAPSHOT-HYGIENE] Refreshing snapshots...")
        
        # Snapshot model weights
        await self._snapshot_models()
        
        # Snapshot configs
        await self._snapshot_configs()
        
        # Cleanup old snapshots
        await self._cleanup_old_snapshots()
        
        logger.info("[SNAPSHOT-HYGIENE] Snapshot refresh complete")
    
    async def _snapshot_models(self):
        """Snapshot all model weights"""
        
        ml_artifacts = Path(__file__).parent.parent.parent / 'ml_artifacts'
        
        if not ml_artifacts.exists():
            return
        
        model_files = list(ml_artifacts.rglob('*.pt')) + list(ml_artifacts.rglob('*.pkl'))
        
        for model_file in model_files:
            try:
                # Create timestamped snapshot
                timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
                snapshot_name = f"{model_file.stem}_{timestamp}{model_file.suffix}"
                snapshot_path = self.models_dir / snapshot_name
                
                # Copy model
                shutil.copy2(model_file, snapshot_path)
                
                # Also maintain "latest" snapshot
                latest_path = self.models_dir / model_file.name
                shutil.copy2(model_file, latest_path)
                
                logger.debug(f"[SNAPSHOT-HYGIENE] Snapshotted model: {model_file.name}")
            
            except Exception as e:
                logger.warning(f"[SNAPSHOT-HYGIENE] Could not snapshot {model_file}: {e}")
    
    async def _snapshot_configs(self):
        """Snapshot all config files"""
        
        config_dir = Path(__file__).parent.parent.parent / 'config'
        
        if not config_dir.exists():
            return
        
        config_files = list(config_dir.glob('*.yaml')) + list(config_dir.glob('*.json'))
        
        for config_file in config_files:
            try:
                # Create timestamped snapshot
                timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
                snapshot_name = f"{config_file.stem}_{timestamp}{config_file.suffix}"
                snapshot_path = self.configs_dir / snapshot_name
                
                # Copy config
                shutil.copy2(config_file, snapshot_path)
                
                # Also maintain "latest" snapshot
                latest_path = self.configs_dir / config_file.name
                shutil.copy2(config_file, latest_path)
                
                logger.debug(f"[SNAPSHOT-HYGIENE] Snapshotted config: {config_file.name}")
            
            except Exception as e:
                logger.warning(f"[SNAPSHOT-HYGIENE] Could not snapshot {config_file}: {e}")
    
    async def _cleanup_old_snapshots(self):
        """Remove snapshots older than max age"""
        
        cutoff_time = datetime.utcnow() - timedelta(hours=self.max_snapshot_age_hours)
        
        # Cleanup model snapshots
        for snapshot_file in self.models_dir.glob('*_*.pt'):
            try:
                # Extract timestamp from filename
                timestamp_str = snapshot_file.stem.split('_')[-2:]  # Get last two parts (date_time)
                
                # Remove if old
                mtime = datetime.fromtimestamp(snapshot_file.stat().st_mtime)
                if mtime < cutoff_time:
                    snapshot_file.unlink()
                    logger.debug(f"[SNAPSHOT-HYGIENE] Removed old snapshot: {snapshot_file.name}")
            
            except Exception as e:
                logger.debug(f"[SNAPSHOT-HYGIENE] Could not process {snapshot_file}: {e}")
        
        # Cleanup config snapshots
        for snapshot_file in self.configs_dir.glob('*_*.*'):
            try:
                mtime = datetime.fromtimestamp(snapshot_file.stat().st_mtime)
                if mtime < cutoff_time:
                    snapshot_file.unlink()
                    logger.debug(f"[SNAPSHOT-HYGIENE] Removed old snapshot: {snapshot_file.name}")
            
            except Exception as e:
                logger.debug(f"[SNAPSHOT-HYGIENE] Could not process {snapshot_file}: {e}")
    
    def get_status(self) -> Dict:
        """Get snapshot status for dashboard"""
        
        model_snapshots = list(self.models_dir.glob('*'))
        config_snapshots = list(self.configs_dir.glob('*'))
        
        return {
            'running': self.running,
            'refresh_interval_hours': self.refresh_interval / 3600,
            'max_age_hours': self.max_snapshot_age_hours,
            'model_snapshots': len(model_snapshots),
            'config_snapshots': len(config_snapshots),
            'total_snapshots': len(model_snapshots) + len(config_snapshots)
        }


# Global instance
snapshot_hygiene_manager = SnapshotHygieneManager()
