"""
Grace Data Cube - Analytical Layer

Provides unified metrics and multi-dimensional slicing across:
- Verification executions
- Error events  
- Approvals
- Mission performance

Architecture:
- Dimensions: Time, Mission, Component, Tier, Actor
- Facts: Verification executions, Error events, Approvals
- ETL: Incremental batch load (5-minute intervals)
- Engine: DuckDB for embedded analytics
- API: REST endpoints for dashboards and ML pipelines
"""

from .etl import cube_etl
from .cube_engine import grace_cube
from .scheduler import start_cube_scheduler, stop_cube_scheduler

__all__ = [
    'cube_etl',
    'grace_cube',
    'start_cube_scheduler',
    'stop_cube_scheduler'
]
