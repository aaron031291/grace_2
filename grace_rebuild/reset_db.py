import asyncio
import os

async def reset():
    if os.path.exists("grace.db"):
        print("Closing all connections...")
        await asyncio.sleep(1)
        
    from backend.models import engine, Base
    from backend.reflection import Reflection
    
    print("Recreating all tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    from backend.models import User, async_session
    from backend.auth import hash_password
    
    async with async_session() as session:
        admin = User(username="admin", password_hash=hash_password("admin123"))
        session.add(admin)
        await session.commit()
    
    print("SUCCESS: Database reset complete!")
    print("SUCCESS: Admin user created: admin / admin123")
    print("\nRestart the backend: py -m uvicorn backend.main:app --reload")

if __name__ == "__main__":
    asyncio.run(reset())
