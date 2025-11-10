"""
Data Cube Schema Definition

Creates dimension and fact tables in the analytical database.
Separate from operational DB to avoid impacting transactional performance.
"""

import asyncio
from sqlalchemy import text
from backend.models import async_session


# Dimension table DDL
DIM_TIME_DDL = """
CREATE TABLE IF NOT EXISTS dim_time (
    time_key INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TIMESTAMP NOT NULL UNIQUE,
    minute INTEGER,
    hour INTEGER,
    day INTEGER,
    week INTEGER,
    month INTEGER,
    quarter INTEGER,
    year INTEGER,
    day_of_week TEXT,
    is_business_hours BOOLEAN,
    is_weekend BOOLEAN
);

CREATE INDEX IF NOT EXISTS idx_dim_time_timestamp ON dim_time(timestamp);
CREATE INDEX IF NOT EXISTS idx_dim_time_day ON dim_time(year, month, day);
"""

DIM_MISSION_DDL = """
CREATE TABLE IF NOT EXISTS dim_mission (
    mission_key INTEGER PRIMARY KEY AUTOINCREMENT,
    mission_id TEXT UNIQUE NOT NULL,
    mission_name TEXT,
    mission_type TEXT,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    final_status TEXT,
    is_current BOOLEAN DEFAULT 1,
    effective_from TIMESTAMP,
    effective_to TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_dim_mission_id ON dim_mission(mission_id);
CREATE INDEX IF NOT EXISTS idx_dim_mission_type ON dim_mission(mission_type);
"""

DIM_COMPONENT_DDL = """
CREATE TABLE IF NOT EXISTS dim_component (
    component_key INTEGER PRIMARY KEY AUTOINCREMENT,
    component_name TEXT UNIQUE NOT NULL,
    subsystem TEXT,
    tier_default TEXT,
    description TEXT
);
"""

DIM_TIER_DDL = """
CREATE TABLE IF NOT EXISTS dim_tier (
    tier_key INTEGER PRIMARY KEY AUTOINCREMENT,
    tier_code TEXT UNIQUE NOT NULL,
    tier_name TEXT,
    requires_approval BOOLEAN,
    requires_snapshot BOOLEAN,
    requires_benchmark BOOLEAN,
    risk_level TEXT,
    description TEXT,
    is_current BOOLEAN DEFAULT 1,
    effective_from TIMESTAMP,
    effective_to TIMESTAMP
);
"""

DIM_ACTOR_DDL = """
CREATE TABLE IF NOT EXISTS dim_actor (
    actor_key INTEGER PRIMARY KEY AUTOINCREMENT,
    actor_id TEXT UNIQUE NOT NULL,
    actor_type TEXT,
    actor_name TEXT,
    is_trusted BOOLEAN DEFAULT 0
);
"""

# Fact table DDL
FACT_VERIFICATION_EXECUTIONS_DDL = """
CREATE TABLE IF NOT EXISTS fact_verification_executions (
    execution_key INTEGER PRIMARY KEY AUTOINCREMENT,
    
    time_key INTEGER,
    mission_key INTEGER,
    component_key INTEGER,
    tier_key INTEGER,
    actor_key INTEGER,
    
    contract_id TEXT,
    action_type TEXT,
    playbook_id TEXT,
    
    duration_seconds REAL,
    confidence_score REAL,
    drift_score REAL,
    
    was_successful BOOLEAN,
    was_rolled_back BOOLEAN,
    created_snapshot BOOLEAN,
    passed_benchmark BOOLEAN,
    
    contract_status TEXT,
    error_message TEXT,
    created_at TIMESTAMP,
    
    FOREIGN KEY (time_key) REFERENCES dim_time(time_key),
    FOREIGN KEY (mission_key) REFERENCES dim_mission(mission_key),
    FOREIGN KEY (component_key) REFERENCES dim_component(component_key),
    FOREIGN KEY (tier_key) REFERENCES dim_tier(tier_key),
    FOREIGN KEY (actor_key) REFERENCES dim_actor(actor_key)
);

CREATE INDEX IF NOT EXISTS idx_fact_ver_time ON fact_verification_executions(time_key);
CREATE INDEX IF NOT EXISTS idx_fact_ver_mission ON fact_verification_executions(mission_key);
CREATE INDEX IF NOT EXISTS idx_fact_ver_tier ON fact_verification_executions(tier_key);
CREATE INDEX IF NOT EXISTS idx_fact_ver_component ON fact_verification_executions(component_key);
CREATE INDEX IF NOT EXISTS idx_fact_ver_created ON fact_verification_executions(created_at);
"""

FACT_ERROR_EVENTS_DDL = """
CREATE TABLE IF NOT EXISTS fact_error_events (
    error_key INTEGER PRIMARY KEY AUTOINCREMENT,
    
    time_key INTEGER,
    component_key INTEGER,
    actor_key INTEGER,
    
    error_id TEXT,
    error_type TEXT,
    severity TEXT,
    source TEXT,
    
    was_auto_resolved BOOLEAN,
    resolution_time_seconds REAL,
    playbook_triggered TEXT,
    required_human_intervention BOOLEAN,
    
    created_at TIMESTAMP,
    
    FOREIGN KEY (time_key) REFERENCES dim_time(time_key),
    FOREIGN KEY (component_key) REFERENCES dim_component(component_key),
    FOREIGN KEY (actor_key) REFERENCES dim_actor(actor_key)
);

CREATE INDEX IF NOT EXISTS idx_fact_err_time ON fact_error_events(time_key);
CREATE INDEX IF NOT EXISTS idx_fact_err_severity ON fact_error_events(severity);
"""

FACT_APPROVALS_DDL = """
CREATE TABLE IF NOT EXISTS fact_approvals (
    approval_key INTEGER PRIMARY KEY AUTOINCREMENT,
    
    time_key INTEGER,
    tier_key INTEGER,
    actor_key INTEGER,
    
    approval_id TEXT,
    approval_type TEXT,
    action_description TEXT,
    
    was_approved BOOLEAN,
    decision_time_seconds REAL,
    risk_score REAL,
    
    created_at TIMESTAMP,
    decided_at TIMESTAMP,
    
    FOREIGN KEY (time_key) REFERENCES dim_time(time_key),
    FOREIGN KEY (tier_key) REFERENCES dim_tier(tier_key),
    FOREIGN KEY (actor_key) REFERENCES dim_actor(actor_key)
);

CREATE INDEX IF NOT EXISTS idx_fact_app_time ON fact_approvals(time_key);
CREATE INDEX IF NOT EXISTS idx_fact_app_tier ON fact_approvals(tier_key);
"""

# ETL metadata table
ETL_METADATA_DDL = """
CREATE TABLE IF NOT EXISTS cube_etl_metadata (
    etl_run_id INTEGER PRIMARY KEY AUTOINCREMENT,
    last_load_timestamp TIMESTAMP NOT NULL,
    records_loaded INTEGER DEFAULT 0,
    duration_seconds REAL,
    status TEXT DEFAULT 'success',
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""


async def create_cube_schema():
    """
    Create all cube tables (dimensions, facts, metadata).
    Safe to run multiple times (idempotent).
    """
    
    print("Creating data cube schema...")
    
    async with async_session() as session:
        # Create dimensions (execute statements one at a time)
        print("  Creating dimension tables...")
        for stmt in DIM_TIME_DDL.split(';'):
            if stmt.strip():
                await session.execute(text(stmt))
        
        for stmt in DIM_MISSION_DDL.split(';'):
            if stmt.strip():
                await session.execute(text(stmt))
        
        for stmt in DIM_COMPONENT_DDL.split(';'):
            if stmt.strip():
                await session.execute(text(stmt))
        
        for stmt in DIM_TIER_DDL.split(';'):
            if stmt.strip():
                await session.execute(text(stmt))
        
        for stmt in DIM_ACTOR_DDL.split(';'):
            if stmt.strip():
                await session.execute(text(stmt))
        
        # Create facts
        print("  Creating fact tables...")
        for stmt in FACT_VERIFICATION_EXECUTIONS_DDL.split(';'):
            if stmt.strip():
                await session.execute(text(stmt))
        
        for stmt in FACT_ERROR_EVENTS_DDL.split(';'):
            if stmt.strip():
                await session.execute(text(stmt))
        
        for stmt in FACT_APPROVALS_DDL.split(';'):
            if stmt.strip():
                await session.execute(text(stmt))
        
        # Create ETL metadata
        print("  Creating ETL metadata table...")
        for stmt in ETL_METADATA_DDL.split(';'):
            if stmt.strip():
                await session.execute(text(stmt))
        
        await session.commit()
    
    # Seed static dimensions
    await seed_static_dimensions()
    
    print("Data cube schema created successfully!")


async def seed_static_dimensions():
    """Populate static dimension tables with known values"""
    
    print("  Seeding static dimensions...")
    
    async with async_session() as session:
        # Seed dim_tier
        await session.execute(text("""
            INSERT OR IGNORE INTO dim_tier (tier_code, tier_name, requires_approval, requires_snapshot, requires_benchmark, risk_level, is_current, effective_from)
            VALUES 
                ('tier_1', 'Operational', 0, 0, 0, 'low', 1, CURRENT_TIMESTAMP),
                ('tier_2', 'Tactical', 0, 1, 1, 'medium', 1, CURRENT_TIMESTAMP),
                ('tier_3', 'Strategic', 1, 1, 1, 'high', 1, CURRENT_TIMESTAMP)
        """))
        
        # Seed dim_component
        await session.execute(text("""
            INSERT OR IGNORE INTO dim_component (component_name, subsystem, tier_default)
            VALUES 
                ('input_sentinel', 'error_handling', 'tier_1'),
                ('action_executor', 'verification', 'tier_2'),
                ('hunter', 'security', 'tier_2'),
                ('cognition_authority', 'cognition', 'tier_1'),
                ('policy_engine', 'governance', 'tier_3'),
                ('shard_orchestrator', 'concurrency', 'tier_1'),
                ('grace_autonomous', 'core', 'tier_1'),
                ('parliament_engine', 'governance', 'tier_3')
        """))
        
        await session.commit()
    
    print("  Static dimensions seeded!")


if __name__ == "__main__":
    asyncio.run(create_cube_schema())
