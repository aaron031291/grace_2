"""
Run initial data cube ETL load
"""

import asyncio
from backend.data_cube.etl import cube_etl


async def main():
    print("=" * 60)
    print("GRACE DATA CUBE - INITIAL ETL LOAD")
    print("=" * 60)
    print()
    
    result = await cube_etl.run_incremental_load()
    
    print()
    print("=" * 60)
    print("ETL COMPLETE")
    print("=" * 60)
    print(f"  Records loaded: {result.get('records_loaded', 0)}")
    print(f"  Duration: {result.get('duration_seconds', 0):.2f}s")
    print(f"  Status: {'SUCCESS' if result.get('success') else 'FAILED'}")


if __name__ == "__main__":
    asyncio.run(main())
