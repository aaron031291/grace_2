"""
Data Cube ETL Pipeline

Incremental batch loading from operational tables to analytical cube.
Runs every 5 minutes to keep cube fresh without impacting operational DB.
"""

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
        
        start_time = datetime.utcnow()
        total_records = 0
        
        try:
            # Load dimensions (idempotent)
            await self._load_dim_time(watermark)
            await self._load_dim_mission(watermark)
            await self._load_dim_actor(watermark)
            
            # Load facts (new records only)
            records = await self._load_fact_verification_executions(watermark)
            total_records += records
            
            records = await self._load_fact_error_events(watermark)
            total_records += records
            
            # Update watermark
            duration = (datetime.utcnow() - start_time).total_seconds()
            await self._update_watermark(datetime.utcnow(), total_records, duration, "success")
            
            print(f"ETL complete! Loaded {total_records} records in {duration:.2f}s")
            return {"success": True, "records_loaded": total_records, "duration_seconds": duration}
            
        except Exception as e:
            duration = (datetime.utcnow() - start_time).total_seconds()
            await self._update_watermark(datetime.utcnow(), 0, duration, "failed", str(e))
            print(f"ETL failed: {e}")
            raise
    
    async def _load_dim_time(self, since: datetime):
        """Generate time dimension entries for new timestamps"""
        
        async with async_session() as session:
            # Get distinct timestamps from fact sources
            result = await session.execute(text("""
                SELECT DISTINCT DATE(created_at) as date_val
                FROM action_contracts
                WHERE created_at >= :since
                UNION
                SELECT DISTINCT DATE(timestamp) as date_val
                FROM immutable_log
                WHERE timestamp >= :since
                LIMIT 1000
            """), {"since": since})
            
            dates = [row[0] for row in result.fetchall()]
            
            for date_val in dates:
                # Insert time dimension row if not exists
                dt = datetime.fromisoformat(date_val) if isinstance(date_val, str) else date_val
                
                await session.execute(text("""
                    INSERT OR IGNORE INTO dim_time (
                        timestamp, minute, hour, day, week, month, quarter, year,
                        day_of_week, is_business_hours, is_weekend
                    )
                    VALUES (
                        :timestamp, :minute, :hour, :day, :week, :month, :quarter, :year,
                        :day_of_week, :is_business_hours, :is_weekend
                    )
                """), {
                    "timestamp": dt,
                    "minute": dt.minute,
                    "hour": dt.hour,
                    "day": dt.day,
                    "week": dt.isocalendar()[1],
                    "month": dt.month,
                    "quarter": (dt.month - 1) // 3 + 1,
                    "year": dt.year,
                    "day_of_week": dt.strftime("%A"),
                    "is_business_hours": 9 <= dt.hour < 17,
                    "is_weekend": dt.weekday() >= 5
                })
            
            await session.commit()
            print(f"  Loaded {len(dates)} time dimension entries")
    
    async def _load_dim_mission(self, since: datetime):
        """Load mission dimension from mission_timelines"""
        
        async with async_session() as session:
            result = await session.execute(text("""
                SELECT 
                    mission_id, mission_name, started_at, completed_at, status
                FROM mission_timelines
                WHERE started_at >= :since
            """), {"since": since})
            
            missions = result.fetchall()
            
            for mission in missions:
                await session.execute(text("""
                    INSERT OR REPLACE INTO dim_mission (
                        mission_id, mission_name, mission_type, started_at, 
                        completed_at, final_status, is_current, effective_from
                    )
                    VALUES (
                        :mission_id, :mission_name, 'error_recovery', :started_at,
                        :completed_at, :status, 1, :started_at
                    )
                """), {
                    "mission_id": mission[0],
                    "mission_name": mission[1],
                    "started_at": mission[2],
                    "completed_at": mission[3],
                    "status": mission[4]
                })
            
            await session.commit()
            print(f"  Loaded {len(missions)} mission dimension entries")
    
    async def _load_dim_actor(self, since: datetime):
        """Load actor dimension from various sources"""
        
        async with async_session() as session:
            # Get distinct actors from operational tables
            result = await session.execute(text("""
                SELECT DISTINCT triggered_by
                FROM action_contracts
                WHERE created_at >= :since AND triggered_by IS NOT NULL
                LIMIT 100
            """), {"since": since})
            
            actors = result.fetchall()
            
            for actor_tuple in actors:
                actor_id = actor_tuple[0]
                if not actor_id:
                    continue
                
                # Parse actor type from ID format
                actor_type = "system"
                if actor_id.startswith("user:"):
                    actor_type = "human"
                elif actor_id.startswith("agent:"):
                    actor_type = "agent"
                
                await session.execute(text("""
                    INSERT OR IGNORE INTO dim_actor (
                        actor_id, actor_type, actor_name, is_trusted
                    )
                    VALUES (:actor_id, :actor_type, :actor_id, 0)
                """), {
                    "actor_id": actor_id,
                    "actor_type": actor_type
                })
            
            await session.commit()
            print(f"  Loaded {len(actors)} actor dimension entries")
    
    async def _load_fact_verification_executions(self, since: datetime) -> int:
        """
        Load verification execution facts from action_contracts
        """
        
        async with async_session() as session:
            # Get new contracts since last load
            result = await session.execute(text("""
                SELECT 
                    id, action_type, tier, created_at, verified_at, executed_at,
                    confidence_score, status, safe_hold_snapshot_id, triggered_by
                FROM action_contracts
                WHERE created_at >= :since
            """), {"since": since})
            
            contracts = result.fetchall()
            
            for contract in contracts:
                contract_id, action_type, tier, created_at, verified_at, executed_at, \
                    confidence_score, status, snapshot_id, triggered_by = contract
                
                # Calculate duration
                duration_seconds = None
                if verified_at and created_at:
                    delta = (verified_at if isinstance(verified_at, datetime) else datetime.fromisoformat(verified_at)) - \
                            (created_at if isinstance(created_at, datetime) else datetime.fromisoformat(created_at))
                    duration_seconds = delta.total_seconds()
                
                # Insert fact row
                await session.execute(text("""
                    INSERT INTO fact_verification_executions (
                        time_key, contract_id, action_type, tier_key,
                        duration_seconds, confidence_score,
                        was_successful, was_rolled_back, created_snapshot,
                        contract_status, created_at
                    )
                    SELECT 
                        t.time_key,
                        :contract_id,
                        :action_type,
                        tier.tier_key,
                        :duration_seconds,
                        :confidence_score,
                        CASE WHEN :status = 'verified' THEN 1 ELSE 0 END,
                        CASE WHEN :status = 'rolled_back' THEN 1 ELSE 0 END,
                        CASE WHEN :snapshot_id IS NOT NULL THEN 1 ELSE 0 END,
                        :status,
                        :created_at
                    FROM dim_time t
                    JOIN dim_tier tier ON tier.tier_code = :tier
                    WHERE DATE(t.timestamp) = DATE(:created_at)
                    LIMIT 1
                """), {
                    'contract_id': contract_id,
                    'action_type': action_type,
                    'tier': tier or 'tier_1',
                    'created_at': created_at,
                    'duration_seconds': duration_seconds,
                    'confidence_score': confidence_score,
                    'status': status,
                    'snapshot_id': snapshot_id
                })
            
            await session.commit()
            print(f"  Loaded {len(contracts)} verification execution facts")
            return len(contracts)
    
    async def _load_fact_error_events(self, since: datetime) -> int:
        """Load error event facts from immutable_log"""
        
        async with async_session() as session:
            # immutable_log doesn't have event_type column, just load recent error-related entries
            result = await session.execute(text("""
                SELECT 
                    id, actor, action, resource, result, timestamp
                FROM immutable_log
                WHERE action LIKE '%error%' OR action LIKE '%fail%'
                AND timestamp >= :since
                LIMIT 1000
            """), {"since": since})
            
            events = result.fetchall()
            
            for event in events:
                event_id, actor, action, resource, result, timestamp = event
                
                await session.execute(text("""
                    INSERT INTO fact_error_events (
                        time_key, error_id, error_type, severity, source,
                        was_auto_resolved, created_at
                    )
                    SELECT 
                        t.time_key,
                        :error_id,
                        :error_type,
                        'medium',
                        :source,
                        0,
                        :timestamp
                    FROM dim_time t
                    WHERE DATE(t.timestamp) = DATE(:timestamp)
                    LIMIT 1
                """), {
                    'error_id': str(event_id),
                    'error_type': action,
                    'source': resource,
                    'timestamp': timestamp
                })
            
            await session.commit()
            print(f"  Loaded {len(events)} error event facts")
            return len(events)
    
    async def _get_last_watermark(self) -> datetime:
        """Get timestamp of last successful ETL run"""
        
        async with async_session() as session:
            result = await session.execute(text("""
                SELECT MAX(last_load_timestamp) 
                FROM cube_etl_metadata
                WHERE status = 'success'
            """))
            watermark = result.scalar()
            
            return watermark or datetime.utcnow() - timedelta(days=7)
    
    async def _update_watermark(self, timestamp: datetime, records: int, duration: float, status: str, error: str = None):
        """Record ETL completion"""
        
        async with async_session() as session:
            await session.execute(text("""
                INSERT INTO cube_etl_metadata (
                    last_load_timestamp, records_loaded, duration_seconds, status, error_message
                )
                VALUES (:timestamp, :records, :duration, :status, :error)
            """), {
                'timestamp': timestamp,
                'records': records,
                'duration': duration,
                'status': status,
                'error': error
            })
            await session.commit()


# Singleton
cube_etl = CubeETL()
