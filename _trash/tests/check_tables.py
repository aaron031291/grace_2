import asyncio
from backend.models import async_session
from sqlalchemy import text

async def main():
    async with async_session() as session:
        result = await session.execute(text("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"))
        tables = [row[0] for row in result.fetchall()]
        
        print("All tables in database:")
        for table in tables:
            print(f"  - {table}")

asyncio.run(main())
