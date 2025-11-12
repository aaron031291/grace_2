#!/usr/bin/env python3
"""
Grace Boot Script - Updated to use unified orchestrator
"""
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from unified_grace_orchestrator import main

if __name__ == "__main__":
    main()

