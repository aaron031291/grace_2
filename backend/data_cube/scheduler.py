"""
Data Cube ETL Scheduler

Runs incremental ETL jobs on a schedule to keep cube fresh.
"""

import asyncio

# Conditional import for apscheduler
try:
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    scheduler = AsyncIOScheduler()
    SCHEDULER_AVAILABLE = True
except ImportError:
    scheduler = None
    SCHEDULER_AVAILABLE = False

from backend.data_cube.etl import cube_etl


async def run_incremental_etl():
    """Run ETL job to refresh cube"""
    try:
        await cube_etl.run_incremental_load()
    except Exception as e:
        print(f"Cube ETL failed: {e}")
        # TODO(FUTURE): Alert on failure


def start_cube_scheduler():
    """Start scheduled ETL jobs"""
    
    # Run every 5 minutes
    scheduler.add_job(
        run_incremental_etl,
        'interval',
        minutes=5,
        id='cube_etl',
        name='Cube ETL (incremental load)',
        replace_existing=True
    )
    
    scheduler.start()
    print("[OK] Cube ETL scheduler started (5-minute intervals)")


def stop_cube_scheduler():
    """Stop scheduler on shutdown"""
    scheduler.shutdown()
    print("[OK] Cube ETL scheduler stopped")
