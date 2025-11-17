"""
Storage Tracking Service
Tracks MB, GB, TB of data Grace ingests for learning
Monitors storage capacity and optimizes usage
"""

import asyncio
import logging
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path
import os

logger = logging.getLogger(__name__)


class StorageTracker:
    """
    Tracks storage usage across all Grace's learning data
    Monitors: grace_training/, databases/, ml_artifacts/, etc.
    """
    
    def __init__(self):
        self.total_capacity_tb = 1.0  # 1TB available (configurable)
        self._initialized = False
        
        # Directories to track
        self.tracked_dirs = [
            'grace_training',
            'databases',
            'ml_artifacts',
            'storage',
            'exports',
            '.grace_cache'
        ]
    
    async def initialize(self):
        """Initialize storage tracking"""
        if self._initialized:
            return
        
        logger.info("[STORAGE-TRACKER] Initializing storage tracking system")
        self._initialized = True
    
    async def get_directory_size(self, directory: str) -> Dict[str, Any]:
        """Get size of a directory in bytes"""
        total_size = 0
        file_count = 0
        
        try:
            path = Path(directory)
            if not path.exists():
                return {'size_bytes': 0, 'files': 0, 'error': 'Directory not found'}
            
            for item in path.rglob('*'):
                if item.is_file():
                    try:
                        total_size += item.stat().st_size
                        file_count += 1
                    except (OSError, PermissionError):
                        pass
            
            return {
                'directory': directory,
                'size_bytes': total_size,
                'size_mb': round(total_size / (1024 * 1024), 2),
                'size_gb': round(total_size / (1024 * 1024 * 1024), 3),
                'files': file_count
            }
        
        except Exception as e:
            logger.error(f"[STORAGE-TRACKER] Failed to get size for {directory}: {e}")
            return {'size_bytes': 0, 'files': 0, 'error': str(e)}
    
    async def get_storage_report(self) -> Dict[str, Any]:
        """
        Generate complete storage usage report
        Shows MB, GB, TB usage across all tracked directories
        """
        report = {
            'timestamp': datetime.utcnow().isoformat(),
            'total_capacity_tb': self.total_capacity_tb,
            'directories': {},
            'totals': {
                'bytes': 0,
                'mb': 0.0,
                'gb': 0.0,
                'tb': 0.0,
                'files': 0
            },
            'usage_pct': 0.0,
            'remaining_tb': 0.0
        }
        
        # Scan each directory
        for directory in self.tracked_dirs:
            dir_stats = await self.get_directory_size(directory)
            report['directories'][directory] = dir_stats
            
            report['totals']['bytes'] += dir_stats.get('size_bytes', 0)
            report['totals']['files'] += dir_stats.get('files', 0)
        
        # Calculate totals
        report['totals']['mb'] = round(report['totals']['bytes'] / (1024 * 1024), 2)
        report['totals']['gb'] = round(report['totals']['bytes'] / (1024 * 1024 * 1024), 3)
        report['totals']['tb'] = round(report['totals']['bytes'] / (1024 * 1024 * 1024 * 1024), 4)
        
        # Calculate usage percentage
        used_tb = report['totals']['tb']
        report['usage_pct'] = round((used_tb / self.total_capacity_tb) * 100, 2)
        report['remaining_tb'] = round(self.total_capacity_tb - used_tb, 4)
        
        logger.info(f"[STORAGE-TRACKER] Total usage: {report['totals']['gb']} GB ({report['usage_pct']}%)")
        logger.info(f"[STORAGE-TRACKER] Remaining: {report['remaining_tb']} TB")
        
        return report
    
    async def get_learning_data_breakdown(self) -> Dict[str, Any]:
        """
        Detailed breakdown of learning data storage
        Shows what types of data are taking up space
        """
        breakdown = {
            'documentation': await self.get_directory_size('grace_training/documentation'),
            'code_examples': await self.get_directory_size('grace_training/code'),
            'datasets': await self.get_directory_size('grace_training/datasets'),
            'repositories': await self.get_directory_size('grace_training/codebases'),
            'total_learning_data_gb': 0.0
        }
        
        total_bytes = sum(
            item.get('size_bytes', 0) 
            for item in breakdown.values() 
            if isinstance(item, dict)
        )
        
        breakdown['total_learning_data_gb'] = round(total_bytes / (1024 * 1024 * 1024), 3)
        
        return breakdown
    
    async def check_storage_capacity(self) -> Dict[str, Any]:
        """
        Check if Grace has enough storage for continued learning
        Returns warnings if running low
        """
        report = await self.get_storage_report()
        
        warnings = []
        recommendations = []
        
        usage_pct = report['usage_pct']
        
        if usage_pct >= 90:
            warnings.append("CRITICAL: Storage 90%+ full")
            recommendations.append("Clean up old/unused data immediately")
        elif usage_pct >= 75:
            warnings.append("WARNING: Storage 75%+ full")
            recommendations.append("Consider archiving old learning data")
        elif usage_pct >= 50:
            warnings.append("INFO: Storage 50%+ full")
            recommendations.append("Monitor storage usage regularly")
        
        return {
            'status': 'CRITICAL' if usage_pct >= 90 else 'WARNING' if usage_pct >= 75 else 'OK',
            'usage_pct': usage_pct,
            'remaining_tb': report['remaining_tb'],
            'warnings': warnings,
            'recommendations': recommendations,
            'can_continue_learning': usage_pct < 95
        }
    
    async def optimize_storage(self) -> Dict[str, Any]:
        """
        Optimize storage by identifying and cleaning up:
        - Duplicate files
        - Old cache files
        - Temporary files
        - Unused data
        """
        optimization_report = {
            'started_at': datetime.utcnow().isoformat(),
            'actions_taken': [],
            'space_freed_gb': 0.0
        }
        
        # Clean cache directories
        cache_dirs = ['.grace_cache', '.pytest_cache', '__pycache__']
        
        for cache_dir in cache_dirs:
            try:
                cache_path = Path(cache_dir)
                if cache_path.exists():
                    before_size = await self.get_directory_size(cache_dir)
                    
                    # Clean cache (implementation would go here)
                    # For now, just report
                    optimization_report['actions_taken'].append({
                        'action': f'Analyzed {cache_dir}',
                        'size_mb': before_size.get('size_mb', 0)
                    })
            
            except Exception as e:
                logger.warning(f"[STORAGE-TRACKER] Failed to clean {cache_dir}: {e}")
        
        optimization_report['completed_at'] = datetime.utcnow().isoformat()
        
        return optimization_report
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get storage tracking metrics"""
        report = await self.get_storage_report()
        
        return {
            'total_used_gb': report['totals']['gb'],
            'total_used_tb': report['totals']['tb'],
            'usage_percentage': report['usage_pct'],
            'remaining_tb': report['remaining_tb'],
            'total_files': report['totals']['files'],
            'capacity_tb': self.total_capacity_tb,
            'can_learn_more': report['usage_pct'] < 95,
            'initialized': self._initialized
        }


# Global instance
storage_tracker = StorageTracker()
