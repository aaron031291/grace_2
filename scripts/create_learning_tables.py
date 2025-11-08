"""Create learning loop tables directly"""

import asyncio
from backend.models import async_session
from sqlalchemy import text


async def create_tables():
    print("Creating learning loop tables...")
    
    async with async_session() as session:
        # outcome_records
        await session.execute(text("""
            CREATE TABLE IF NOT EXISTS outcome_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contract_id TEXT,
                playbook_id TEXT,
                action_type TEXT,
                error_pattern TEXT,
                diagnosis_code TEXT,
                success BOOLEAN,
                confidence_score REAL,
                execution_time_seconds REAL,
                problem_resolved BOOLEAN,
                rollback_occurred BOOLEAN,
                tier TEXT,
                triggered_by TEXT,
                context TEXT,
                created_at TIMESTAMP
            )
        """))
        
        await session.execute(text("""
            CREATE INDEX IF NOT EXISTS ix_outcome_records_playbook_id ON outcome_records(playbook_id)
        """))
        
        await session.execute(text("""
            CREATE INDEX IF NOT EXISTS ix_outcome_records_error_pattern ON outcome_records(error_pattern)
        """))
        
        await session.execute(text("""
            CREATE INDEX IF NOT EXISTS ix_outcome_records_created_at ON outcome_records(created_at)
        """))
        
        # playbook_statistics  
        await session.execute(text("DROP TABLE IF EXISTS playbook_statistics"))
        
        await session.execute(text("""
            CREATE TABLE playbook_statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                playbook_id TEXT UNIQUE,
                total_executions INTEGER DEFAULT 0,
                successful_executions INTEGER DEFAULT 0,
                failed_executions INTEGER DEFAULT 0,
                rollbacks INTEGER DEFAULT 0,
                avg_confidence_score REAL DEFAULT 0.0,
                avg_execution_time REAL DEFAULT 0.0,
                success_rate REAL DEFAULT 0.0,
                last_success_at TIMESTAMP,
                last_failure_at TIMESTAMP,
                recommended_for_patterns TEXT,
                updated_at TIMESTAMP
            )
        """))
        
        await session.execute(text("""
            CREATE INDEX IF NOT EXISTS ix_playbook_statistics_success_rate ON playbook_statistics(success_rate)
        """))
        
        await session.commit()
    
    print("  [OK] outcome_records")
    print("  [OK] playbook_statistics")
    print("\nLearning tables created successfully!")


if __name__ == "__main__":
    asyncio.run(create_tables())
