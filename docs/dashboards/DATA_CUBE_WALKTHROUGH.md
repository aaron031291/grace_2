# Grace Data Cube - Complete Walkthrough

**Purpose**: Single source of truth for all verification, error, and execution metrics  
**Status**: Design → Implementation  
**Date**: 2025-11-07

---

## 🎯 Why a Data Cube?

### The Problem Today
- Metrics scattered across 12+ operational tables
- Each dashboard joins differently → inconsistent numbers
- Ad-hoc queries slow (3+ table joins every time)
- ML pipelines duplicate aggregation logic
- No historical trending without custom ETL

### The Solution: Shared Analytical Cube
- **One canonical metric**: "verification success rate" means the same everywhere
- **Pre-aggregated**: Mission × Tier × Outcome pre-computed
- **Multi-dimensional slicing**: Instant pivots without joins
- **Historical tracking**: Built-in time series
- **ML-ready**: Features extracted once, reused everywhere

---

## 📊 Phase 1: Baseline Inventory

### Raw Data Sources (Current State)

```
Verification System (LIVE):
├─ action_contracts       → Contract execution records
├─ safe_hold_snapshots    → Rollback snapshots
├─ benchmark_runs         → Regression test results
└─ mission_timelines      → Multi-action progression

Error System (LIVE):
├─ immutable_log          → All agentic events
├─ security_events        → Hunter alerts
└─ agentic_insights       → Error patterns

Execution System (LIVE):
├─ playbook_runs          → Self-heal playbook executions
├─ playbook_step_runs     → Individual action steps
└─ healing_actions        → Remediation actions

Governance (LIVE):
├─ approval_requests      → Human-in-loop approvals
├─ governance_votes       → Parliament decisions
└─ constitutional_compliance → Policy violations

Shard System (ACTIVE):
├─ execution_tasks        → Concurrent executor queue
└─ (future) shard_heartbeats → Multi-agent telemetry
```

### Data Grain Definition

| Source | Grain | Update Frequency |
|--------|-------|------------------|
| action_contracts | One contract execution | Real-time (per action) |
| benchmark_runs | One benchmark suite run | Real-time (post-action) |
| immutable_log | One event | Real-time (streaming) |
| playbook_runs | One playbook execution | Real-time (per error) |
| approval_requests | One approval decision | Minutes (human latency) |
| mission_timelines | One mission | Hours (multi-action) |

---

## 📐 Phase 2: Core Dimensions

### Dimension: Time
**Grain**: Minute-level resolution  
**Purpose**: All temporal analysis

```sql
CREATE TABLE dim_time (
    time_key INTEGER PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    minute INTEGER,
    hour INTEGER,
    day INTEGER,
    week INTEGER,
    month INTEGER,
    quarter INTEGER,
    year INTEGER,
    day_of_week TEXT,
    is_business_hours BOOLEAN,
    is_weekend BOOLEAN,
    UNIQUE(timestamp)
);

-- Index for range queries
CREATE INDEX idx_dim_time_timestamp ON dim_time(timestamp);
CREATE INDEX idx_dim_time_day ON dim_time(year, month, day);
```

**Generated from**: Existing timestamps in source tables

---

### Dimension: Mission
**Grain**: One row per unique mission  
**Purpose**: Group multi-action workflows

```sql
CREATE TABLE dim_mission (
    mission_key INTEGER PRIMARY KEY AUTOINCREMENT,
    mission_id TEXT UNIQUE NOT NULL,
    mission_name TEXT,
    mission_type TEXT,  -- "error_recovery", "scheduled_task", "user_request"
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    final_status TEXT,  -- "success", "failed", "partial", "rolled_back"
    is_current BOOLEAN DEFAULT 1,  -- SCD Type 2
    effective_from TIMESTAMP,
    effective_to TIMESTAMP
);

CREATE INDEX idx_dim_mission_id ON dim_mission(mission_id);
CREATE INDEX idx_dim_mission_type ON dim_mission(mission_type);
```

**Source**: `mission_timelines` table

---

### Dimension: Component
**Grain**: One row per system component  
**Purpose**: Track which part of Grace triggered/executed

```sql
CREATE TABLE dim_component (
    component_key INTEGER PRIMARY KEY AUTOINCREMENT,
    component_name TEXT UNIQUE NOT NULL,  -- "input_sentinel", "action_executor", "hunter"
    subsystem TEXT,  -- "verification", "security", "cognition"
    tier_default TEXT,  -- Default autonomy tier for this component
    description TEXT
);

-- Pre-populated with known components
INSERT INTO dim_component (component_name, subsystem, tier_default) VALUES
    ('input_sentinel', 'error_handling', 'tier_1'),
    ('action_executor', 'verification', 'tier_2'),
    ('hunter', 'security', 'tier_2'),
    ('cognition_authority', 'cognition', 'tier_1'),
    ('policy_engine', 'governance', 'tier_3'),
    ('shard_orchestrator', 'concurrency', 'tier_1');
```

---

### Dimension: Tier
**Grain**: One row per autonomy tier  
**Purpose**: Slice metrics by risk level

```sql
CREATE TABLE dim_tier (
    tier_key INTEGER PRIMARY KEY AUTOINCREMENT,
    tier_code TEXT UNIQUE NOT NULL,  -- "tier_1", "tier_2", "tier_3"
    tier_name TEXT,  -- "Operational", "Tactical", "Strategic"
    requires_approval BOOLEAN,
    requires_snapshot BOOLEAN,
    requires_benchmark BOOLEAN,
    risk_level TEXT,  -- "low", "medium", "high"
    description TEXT,
    
    -- SCD Type 2 for policy changes
    is_current BOOLEAN DEFAULT 1,
    effective_from TIMESTAMP,
    effective_to TIMESTAMP
);

INSERT INTO dim_tier (tier_code, tier_name, requires_approval, requires_snapshot, requires_benchmark, risk_level) VALUES
    ('tier_1', 'Operational', 0, 0, 0, 'low'),
    ('tier_2', 'Tactical', 0, 1, 1, 'medium'),
    ('tier_3', 'Strategic', 1, 1, 1, 'high');
```

---

### Dimension: Actor
**Grain**: One row per actor (user, agent, system)  
**Purpose**: Track who/what initiated actions

```sql
CREATE TABLE dim_actor (
    actor_key INTEGER PRIMARY KEY AUTOINCREMENT,
    actor_id TEXT UNIQUE NOT NULL,  -- "user:alice", "system:sentinel", "agent:shard_3"
    actor_type TEXT,  -- "human", "system", "agent"
    actor_name TEXT,
    is_trusted BOOLEAN DEFAULT 0
);
```

---

## 📊 Phase 3: Fact Tables

### Fact: Verification Executions
**Grain**: One row per verified action execution  
**Measures**: Duration, confidence, success, drift

```sql
CREATE TABLE fact_verification_executions (
    execution_key INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Foreign keys to dimensions
    time_key INTEGER REFERENCES dim_time(time_key),
    mission_key INTEGER REFERENCES dim_mission(mission_key),
    component_key INTEGER REFERENCES dim_component(component_key),
    tier_key INTEGER REFERENCES dim_tier(tier_key),
    actor_key INTEGER REFERENCES dim_actor(actor_key),
    
    -- Degenerate dimensions (low cardinality, no lookup needed)
    contract_id TEXT,
    action_type TEXT,
    playbook_id TEXT,
    
    -- Measures (numeric facts)
    duration_seconds REAL,
    confidence_score REAL,  -- 0.0 to 1.0
    drift_score REAL,       -- Benchmark deviation
    
    -- Flags (boolean measures)
    was_successful BOOLEAN,
    was_rolled_back BOOLEAN,
    created_snapshot BOOLEAN,
    passed_benchmark BOOLEAN,
    
    -- Metadata
    contract_status TEXT,
    error_message TEXT,
    created_at TIMESTAMP
);

-- Indexes for common slices
CREATE INDEX idx_fact_ver_time ON fact_verification_executions(time_key);
CREATE INDEX idx_fact_ver_mission ON fact_verification_executions(mission_key);
CREATE INDEX idx_fact_ver_tier ON fact_verification_executions(tier_key);
CREATE INDEX idx_fact_ver_component ON fact_verification_executions(component_key);
```

**ETL Source**:
```sql
-- Populate from action_contracts
INSERT INTO fact_verification_executions (
    time_key, mission_key, component_key, tier_key,
    contract_id, action_type, duration_seconds, confidence_score,
    was_successful, was_rolled_back, created_snapshot
)
SELECT 
    t.time_key,
    m.mission_key,
    c.component_key,
    tier.tier_key,
    ac.id AS contract_id,
    ac.action_type,
    JULIANDAY(ac.verified_at) - JULIANDAY(ac.created_at) AS duration_seconds,
    ac.confidence_score,
    CASE WHEN ac.status = 'verified' THEN 1 ELSE 0 END AS was_successful,
    CASE WHEN ac.status = 'rolled_back' THEN 1 ELSE 0 END AS was_rolled_back,
    CASE WHEN ac.safe_hold_snapshot_id IS NOT NULL THEN 1 ELSE 0 END AS created_snapshot
FROM action_contracts ac
LEFT JOIN dim_time t ON DATE(t.timestamp) = DATE(ac.created_at)
LEFT JOIN dim_mission m ON m.mission_id = SUBSTRING(ac.triggered_by, INSTR(ac.triggered_by, ':') + 1)
LEFT JOIN dim_component c ON c.component_name = 'action_executor'
LEFT JOIN dim_tier tier ON tier.tier_code = ac.tier
WHERE ac.created_at >= ?;  -- Incremental load
```

---

### Fact: Error Events
**Grain**: One row per error captured  
**Measures**: Count, severity, resolution time

```sql
CREATE TABLE fact_error_events (
    error_key INTEGER PRIMARY KEY AUTOINCREMENT,
    
    time_key INTEGER REFERENCES dim_time(time_key),
    component_key INTEGER REFERENCES dim_component(component_key),
    actor_key INTEGER REFERENCES dim_actor(actor_key),
    
    error_id TEXT,
    error_type TEXT,
    severity TEXT,  -- "low", "medium", "high", "critical"
    source TEXT,
    
    was_auto_resolved BOOLEAN,
    resolution_time_seconds REAL,
    playbook_triggered TEXT,
    required_human_intervention BOOLEAN,
    
    created_at TIMESTAMP
);
```

---

### Fact: Approvals
**Grain**: One row per approval decision  
**Measures**: Decision time, approval rate

```sql
CREATE TABLE fact_approvals (
    approval_key INTEGER PRIMARY KEY AUTOINCREMENT,
    
    time_key INTEGER REFERENCES dim_time(time_key),
    tier_key INTEGER REFERENCES dim_tier(tier_key),
    actor_key INTEGER REFERENCES dim_actor(actor_key),  -- Approver
    
    approval_id TEXT,
    approval_type TEXT,
    action_description TEXT,
    
    was_approved BOOLEAN,
    decision_time_seconds REAL,
    risk_score REAL,
    
    created_at TIMESTAMP,
    decided_at TIMESTAMP
);
```

---

## 🔧 Phase 4: ETL / Ingestion

### Strategy: Incremental Load

```python
# backend/data_cube/etl.py

import asyncio
from datetime import datetime, timedelta
from sqlalchemy import select, text
from backend.models import async_session

class CubeETL:
    """
    ETL pipeline to populate data cube from operational tables.
    Runs incrementally to keep cube fresh without full rebuilds.
    """
    
    def __init__(self):
        self.last_load_timestamp = None
    
    async def run_incremental_load(self):
        """Load new data since last ETL run"""
        
        # Determine watermark
        watermark = await self._get_last_watermark()
        
        print(f"Running ETL from {watermark}...")
        
        # Load dimensions (idempotent)
        await self._load_dim_time(watermark)
        await self._load_dim_mission(watermark)
        await self._load_dim_component()  # Static
        await self._load_dim_tier()        # Static
        await self._load_dim_actor(watermark)
        
        # Load facts (new records only)
        await self._load_fact_verification_executions(watermark)
        await self._load_fact_error_events(watermark)
        await self._load_fact_approvals(watermark)
        
        # Update watermark
        await self._update_watermark(datetime.utcnow())
        
        print("ETL complete!")
    
    async def _load_fact_verification_executions(self, since: datetime):
        """
        Load verification execution facts from action_contracts
        """
        
        async with async_session() as session:
            # Get new contracts since last load
            from backend.action_contract import ActionContract
            
            stmt = select(ActionContract).where(
                ActionContract.created_at >= since
            )
            result = await session.execute(stmt)
            contracts = result.scalars().all()
            
            for contract in contracts:
                # Insert fact row
                await session.execute(text("""
                    INSERT INTO fact_verification_executions (
                        time_key, contract_id, action_type, tier_key,
                        duration_seconds, confidence_score,
                        was_successful, was_rolled_back, created_snapshot,
                        created_at
                    )
                    SELECT 
                        t.time_key,
                        :contract_id,
                        :action_type,
                        tier.tier_key,
                        CAST((JULIANDAY(:verified_at) - JULIANDAY(:created_at)) * 86400 AS REAL),
                        :confidence_score,
                        CASE WHEN :status = 'verified' THEN 1 ELSE 0 END,
                        CASE WHEN :status = 'rolled_back' THEN 1 ELSE 0 END,
                        CASE WHEN :snapshot_id IS NOT NULL THEN 1 ELSE 0 END,
                        :created_at
                    FROM dim_time t
                    JOIN dim_tier tier ON tier.tier_code = :tier
                    WHERE t.timestamp = :created_at
                    LIMIT 1
                """), {
                    'contract_id': contract.id,
                    'action_type': contract.action_type,
                    'tier': contract.tier,
                    'created_at': contract.created_at,
                    'verified_at': contract.verified_at or contract.created_at,
                    'confidence_score': contract.confidence_score,
                    'status': contract.status,
                    'snapshot_id': contract.safe_hold_snapshot_id
                })
            
            await session.commit()
            print(f"  Loaded {len(contracts)} verification executions")
    
    async def _get_last_watermark(self) -> datetime:
        """Get timestamp of last successful ETL run"""
        
        async with async_session() as session:
            result = await session.execute(text("""
                SELECT MAX(last_load_timestamp) 
                FROM cube_etl_metadata
            """))
            watermark = result.scalar()
            
            return watermark or datetime.utcnow() - timedelta(days=7)
    
    async def _update_watermark(self, timestamp: datetime):
        """Record successful ETL completion"""
        
        async with async_session() as session:
            await session.execute(text("""
                INSERT INTO cube_etl_metadata (last_load_timestamp)
                VALUES (:timestamp)
            """), {'timestamp': timestamp})
            await session.commit()


# Singleton
cube_etl = CubeETL()
```

---

## 📦 Phase 5: Materialize the Cube

### Option A: DuckDB (Embedded Analytics)

```python
# backend/data_cube/cube_engine.py

import duckdb
from pathlib import Path

class GraceCube:
    """
    Analytical cube powered by DuckDB.
    Provides fast multi-dimensional slicing without impacting operational DB.
    """
    
    def __init__(self, cube_path: str = "./databases/grace_cube.duckdb"):
        self.cube_path = Path(cube_path)
        self.conn = duckdb.connect(str(self.cube_path))
        self._init_cube()
    
    def _init_cube(self):
        """Create cube schema and materialized views"""
        
        # Create rollup: Daily verification metrics by tier
        self.conn.execute("""
            CREATE OR REPLACE VIEW cube_daily_verification_by_tier AS
            SELECT 
                t.year,
                t.month,
                t.day,
                tier.tier_name,
                COUNT(*) AS total_executions,
                SUM(CAST(was_successful AS INTEGER)) AS successful_executions,
                AVG(confidence_score) AS avg_confidence,
                AVG(duration_seconds) AS avg_duration_seconds,
                SUM(CAST(was_rolled_back AS INTEGER)) AS rollbacks
            FROM fact_verification_executions f
            JOIN dim_time t ON f.time_key = t.time_key
            JOIN dim_tier tier ON f.tier_key = tier.tier_key
            GROUP BY t.year, t.month, t.day, tier.tier_name
        """)
        
        # Create rollup: Mission success rate
        self.conn.execute("""
            CREATE OR REPLACE VIEW cube_mission_metrics AS
            SELECT 
                m.mission_type,
                tier.tier_name,
                COUNT(DISTINCT m.mission_id) AS total_missions,
                COUNT(DISTINCT CASE WHEN m.final_status = 'success' THEN m.mission_id END) AS successful_missions,
                AVG(f.confidence_score) AS avg_confidence
            FROM dim_mission m
            JOIN fact_verification_executions f ON m.mission_key = f.mission_key
            JOIN dim_tier tier ON f.tier_key = tier.tier_key
            GROUP BY m.mission_type, tier.tier_name
        """)
    
    def get_verification_success_rate(self, tier: str = None, days: int = 7):
        """
        Get verification success rate, optionally filtered by tier
        """
        
        query = """
            SELECT 
                tier.tier_name,
                COUNT(*) AS total,
                SUM(CAST(was_successful AS INTEGER)) AS successful,
                ROUND(100.0 * SUM(CAST(was_successful AS INTEGER)) / COUNT(*), 2) AS success_rate_pct
            FROM fact_verification_executions f
            JOIN dim_tier tier ON f.tier_key = tier.tier_key
            JOIN dim_time t ON f.time_key = t.time_key
            WHERE t.timestamp >= CURRENT_TIMESTAMP - INTERVAL '? days'
        """
        
        if tier:
            query += " AND tier.tier_code = ?"
            result = self.conn.execute(query, [days, tier]).fetchdf()
        else:
            query += " GROUP BY tier.tier_name"
            result = self.conn.execute(query, [days]).fetchdf()
        
        return result.to_dict('records')


# Singleton
grace_cube = GraceCube()
```

---

## 🌐 Phase 6: Expose & Govern

### REST API for Cube Access

```python
# backend/routes/cube_api.py

from fastapi import APIRouter, Depends, Query
from typing import Optional, List
from datetime import date
from pydantic import BaseModel
from backend.data_cube.cube_engine import grace_cube
from backend.auth import get_current_user

router = APIRouter(prefix="/api/cube", tags=["analytics"])


class VerificationMetrics(BaseModel):
    tier_name: str
    total: int
    successful: int
    success_rate_pct: float


@router.get("/metrics/verification-success-rate", response_model=List[VerificationMetrics])
async def get_verification_success_rate(
    tier: Optional[str] = Query(None, regex="^tier_[123]$"),
    days: int = Query(7, ge=1, le=90),
    current_user: str = Depends(get_current_user)
):
    """
    Get verification success rate by tier.
    
    **Governance**: Tier 1+ autonomy required (read-only analytics)
    """
    
    metrics = grace_cube.get_verification_success_rate(tier=tier, days=days)
    return metrics


@router.get("/metrics/mission-performance")
async def get_mission_performance(
    mission_type: Optional[str] = None,
    current_user: str = Depends(get_current_user)
):
    """
    Get mission completion metrics.
    """
    
    query = """
        SELECT * FROM cube_mission_metrics
    """
    
    if mission_type:
        query += " WHERE mission_type = ?"
        result = grace_cube.conn.execute(query, [mission_type]).fetchdf()
    else:
        result = grace_cube.conn.execute(query).fetchdf()
    
    return result.to_dict('records')


@router.get("/metrics/error-trends")
async def get_error_trends(
    days: int = Query(7, ge=1, le=90),
    current_user: str = Depends(get_current_user)
):
    """
    Get error event trends over time.
    """
    
    result = grace_cube.conn.execute("""
        SELECT 
            t.year,
            t.month,
            t.day,
            e.severity,
            COUNT(*) AS error_count,
            SUM(CAST(was_auto_resolved AS INTEGER)) AS auto_resolved_count
        FROM fact_error_events e
        JOIN dim_time t ON e.time_key = t.time_key
        WHERE t.timestamp >= CURRENT_TIMESTAMP - INTERVAL '? days'
        GROUP BY t.year, t.month, t.day, e.severity
        ORDER BY t.year, t.month, t.day
    """, [days]).fetchdf()
    
    return result.to_dict('records')
```

---

## 🔄 Phase 7: Iterate & Automate

### Scheduled ETL Job

```python
# backend/data_cube/scheduler.py

import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from backend.data_cube.etl import cube_etl

scheduler = AsyncIOScheduler()


async def run_incremental_etl():
    """Run ETL job to refresh cube"""
    try:
        await cube_etl.run_incremental_load()
    except Exception as e:
        print(f"ETL failed: {e}")
        # TODO: Alert on failure


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
    print("Cube ETL scheduler started (5-minute intervals)")


def stop_cube_scheduler():
    """Stop scheduler on shutdown"""
    scheduler.shutdown()
```

---

## 📊 Value Realization Timeline

### Week 1: Foundation (You Are Here)
- ✅ Verification tables exist
- ✅ Operational data flowing
- 🔄 Design cube schema (dimensions + facts)
- 🔄 Create ETL pipeline

### Week 2: Initial Cube
- Build DuckDB cube
- Implement basic ETL (verification + error facts)
- Create cube API endpoints
- First dashboard: Verification success rate

### Week 3: Expand Coverage
- Add approval facts
- Add mission performance metrics
- Implement scheduled ETL (5-min refresh)
- Dashboard: Error trends, approval latency

### Week 4: ML Integration
- Export cube data for training
- Feature engineering from cube metrics
- Feedback loop: Learning pipeline writes to cube
- Alert rules based on cube metrics

### Month 2: Production Analytics
- Real-time streaming ETL (not just batch)
- Multi-user dashboards
- Custom metric definitions
- Governance: Access controls by tier

---

## 🎯 Success Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Query latency (p95) | <100ms | N/A (not built) |
| ETL freshness | <5 min lag | N/A |
| Dashboard consistency | 100% (same numbers everywhere) | ~60% (ad-hoc queries) |
| ML feature reuse | >80% from cube | 0% (custom extraction) |
| Analyst self-service | >90% queries without eng help | ~10% |

---

## 🚀 Getting Started

### Immediate Next Steps

1. **Create cube schema**:
   ```bash
   .venv\Scripts\python.exe -c "from backend.data_cube.schema import create_cube_schema; create_cube_schema()"
   ```

2. **Run initial ETL**:
   ```bash
   .venv\Scripts\python.exe -c "from backend.data_cube.etl import cube_etl; import asyncio; asyncio.run(cube_etl.run_incremental_load())"
   ```

3. **Test cube queries**:
   ```bash
   curl http://localhost:8000/api/cube/metrics/verification-success-rate?days=7
   ```

4. **Build first dashboard**:
   - Grafana pointing at cube API
   - Or simple HTML/JS dashboard
   - Key metric: Verification success rate by tier

---

## 💡 Key Insights

1. **Start small**: Verification + Error facts first, expand later
2. **Incremental ETL**: 5-minute batches, not real-time (yet)
3. **DuckDB is enough**: Embedded analytics, no infra overhead
4. **API-first**: Dashboards consume APIs, not direct SQL
5. **Governance built-in**: Access controls aligned with autonomy tiers

**The cube pays off once real data flows. Until then, it's infrastructure ready for the day verified actions go live at scale.**
