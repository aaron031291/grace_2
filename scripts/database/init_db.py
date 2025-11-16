"""
One-time script to initialize the database and create all tables.
"""
import asyncio
import sys
import os

# Add project root to the Python path to allow imports from backend
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import all models so they are registered with the Base
from backend.models.base_models import Base, engine
from backend.models.remote_access_models import RemoteSession, CommandHistory
from backend.learning_systems.learning_loop import OutcomeRecord, PlaybookStatistics

async def create_tables():
    print("Connecting to database...")
    async with engine.begin() as conn:
        print("Dropping all existing tables...")
        await conn.run_sync(Base.metadata.drop_all)
        print("Creating all tables...")
        await conn.run_sync(Base.metadata.create_all)
        print("Tables created successfully.")

if __name__ == "__main__":
    print("Initializing database...")
    asyncio.run(create_tables())