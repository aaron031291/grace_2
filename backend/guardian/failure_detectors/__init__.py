"""
Failure Detectors for Self-Healing System
Each detector monitors a specific failure mode
"""

from .db_connection_detector import DatabaseConnectionDetector
from .api_timeout_detector import APITimeoutDetector

__all__ = [
    'DatabaseConnectionDetector',
    'APITimeoutDetector',
]
