#!/usr/bin/env python3
"""
Grace Snapshot Cleanup Script

Automatically removes old snapshots while keeping:
- The N most recent successful boot snapshots
- The N most recent boot cache directories
- All snapshots created in the last 24 hours (safety buffer)

Usage:
    python scripts/cleanup_snapshots.py --keep 5 --dry-run
    python scripts/cleanup_snapshots.py --keep 3
"""

import argparse
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(description='Clean up old Grace snapshots')
    parser.add_argument(
        '--keep',
        type=int,
        default=5,
        help='Number of recent snapshots to keep (default: 5)'
    )
    parser.add_argument(
        '--keep-days',
        type=int,
        default=7,
        help='Keep all snapshots from the last N days (default: 7)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be deleted without actually deleting'
    )
    return parser.parse_args()


def get_snapshot_age(snapshot_dir: Path) -> datetime | None:
    """Extract creation time from snapshot directory name or metadata"""
    # Try to parse from directory name (boot-ok-2025-11-20_20-39-40)
    if snapshot_dir.name.startswith('boot-ok-'):
        try:
            date_str = snapshot_dir.name.replace('boot-ok-', '')
            return datetime.strptime(date_str, '%Y-%m-%d_%H-%M-%S')
        except ValueError:
            pass
    
    # Try to parse from boot cache timestamp (boot_1763237678_cache)
    if '_cache' in snapshot_dir.name or '_db.sqlite' in snapshot_dir.name:
        try:
            timestamp = int(snapshot_dir.name.split('_')[1])
            return datetime.fromtimestamp(timestamp)
        except (IndexError, ValueError):
            pass
    
    # Fall back to file modification time
    return datetime.fromtimestamp(snapshot_dir.stat().st_mtime)


def cleanup_snapshots(snapshots_dir: Path, keep_count: int, keep_days: int, dry_run: bool = False):
    """Remove old snapshots, keeping the most recent ones"""
    
    if not snapshots_dir.exists():
        logger.warning(f"Snapshots directory not found: {snapshots_dir}")
        return
    
    # Gather all snapshot directories and files
    boot_ok_dirs = sorted(
        [d for d in snapshots_dir.glob('boot-ok-*') if d.is_dir()],
        key=lambda d: get_snapshot_age(d) or datetime.min,
        reverse=True
    )
    
    cache_dirs = sorted(
        [d for d in snapshots_dir.glob('boot_*_cache') if d.is_dir()],
        key=lambda d: get_snapshot_age(d) or datetime.min,
        reverse=True
    )
    
    db_files = sorted(
        [f for f in snapshots_dir.glob('boot_*_db.sqlite')],
        key=lambda f: get_snapshot_age(f.parent) or datetime.min,
        reverse=True
    )
    
    metadata_files = sorted(
        [f for f in snapshots_dir.glob('boot_*_metadata.json')],
        key=lambda f: get_snapshot_age(f.parent) or datetime.min,
        reverse=True
    )
    
    cutoff_date = datetime.now() - timedelta(days=keep_days)
    
    total_deleted = 0
    total_size_freed = 0
    
    # Clean up boot-ok snapshots
    for i, snapshot_dir in enumerate(boot_ok_dirs):
        age = get_snapshot_age(snapshot_dir)
        
        # Keep if within keep_count or keep_days
        if i < keep_count or (age and age > cutoff_date):
            logger.info(f"✓ Keeping: {snapshot_dir.name}")
            continue
        
        # Calculate size before deletion
        size = sum(f.stat().st_size for f in snapshot_dir.rglob('*') if f.is_file())
        
        if dry_run:
            logger.info(f"[DRY RUN] Would delete: {snapshot_dir.name} ({size / 1024 / 1024:.2f} MB)")
        else:
            logger.info(f"🗑️ Deleting: {snapshot_dir.name} ({size / 1024 / 1024:.2f} MB)")
            shutil.rmtree(snapshot_dir)
            total_deleted += 1
            total_size_freed += size
    
    # Clean up cache directories
    for i, cache_dir in enumerate(cache_dirs):
        age = get_snapshot_age(cache_dir)
        
        if i < keep_count or (age and age > cutoff_date):
            continue
        
        size = sum(f.stat().st_size for f in cache_dir.rglob('*') if f.is_file())
        
        if dry_run:
            logger.info(f"[DRY RUN] Would delete: {cache_dir.name} ({size / 1024:.2f} KB)")
        else:
            logger.info(f"🗑️ Deleting: {cache_dir.name} ({size / 1024:.2f} KB)")
            shutil.rmtree(cache_dir)
            total_deleted += 1
            total_size_freed += size
    
    # Clean up orphaned db.sqlite and metadata files
    for i, db_file in enumerate(db_files):
        if i < keep_count:
            continue
        
        if dry_run:
            logger.info(f"[DRY RUN] Would delete: {db_file.name}")
        else:
            logger.info(f"🗑️ Deleting: {db_file.name}")
            db_file.unlink()
            total_deleted += 1
    
    for i, meta_file in enumerate(metadata_files):
        if i < keep_count:
            continue
        
        if dry_run:
            logger.info(f"[DRY RUN] Would delete: {meta_file.name}")
        else:
            logger.info(f"🗑️ Deleting: {meta_file.name}")
            meta_file.unlink()
            total_deleted += 1
    
    if not dry_run:
        logger.info(f"\n✅ Cleanup complete!")
        logger.info(f"   Deleted: {total_deleted} items")
        logger.info(f"   Freed: {total_size_freed / 1024 / 1024:.2f} MB")
    else:
        logger.info(f"\n[DRY RUN] Would delete {total_deleted} items")


def main():
    args = parse_args()
    
    # Find snapshots directory
    project_root = Path(__file__).parent.parent
    snapshots_dir = project_root / '.grace_snapshots'
    
    logger.info(f"Grace Snapshot Cleanup")
    logger.info(f"Snapshots directory: {snapshots_dir}")
    logger.info(f"Keep count: {args.keep}")
    logger.info(f"Keep days: {args.keep_days}")
    logger.info(f"Dry run: {args.dry_run}\n")
    
    cleanup_snapshots(snapshots_dir, args.keep, args.keep_days, args.dry_run)


if __name__ == '__main__':
    main()
