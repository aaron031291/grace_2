"""
Grace Analytical Cube Engine

Provides fast multi-dimensional slicing over pre-aggregated metrics.
Uses the same underlying database but exposes analytical views.
"""

from typing import Dict, List, Optional, Any
from sqlalchemy import text
from backend.models import async_session


class GraceCube:
    """
    Analytical cube for Grace metrics.
    Provides fast multi-dimensional slicing without complex joins.
    """
    
    async def get_verification_success_rate(
        self, 
        tier: Optional[str] = None, 
        days: int = 7
    ) -> List[Dict[str, Any]]:
        """
        Get verification success rate, optionally filtered by tier
        
        Args:
            tier: Filter by tier code (tier_1, tier_2, tier_3)
            days: Number of days to look back
            
        Returns:
            List of metrics by tier
        """
        
        async with async_session() as session:
            if tier:
                result = await session.execute(text("""
                    SELECT 
                        tier.tier_name,
                        COUNT(*) AS total,
                        SUM(CAST(was_successful AS INTEGER)) AS successful,
                        ROUND(100.0 * SUM(CAST(was_successful AS INTEGER)) / COUNT(*), 2) AS success_rate_pct,
                        AVG(confidence_score) AS avg_confidence
                    FROM fact_verification_executions f
                    JOIN dim_tier tier ON f.tier_key = tier.tier_key
                    JOIN dim_time t ON f.time_key = t.time_key
                    WHERE t.timestamp >= datetime('now', '-' || :days || ' days')
                    AND tier.tier_code = :tier
                    GROUP BY tier.tier_name
                """), {"days": days, "tier": tier})
            else:
                result = await session.execute(text("""
                    SELECT 
                        tier.tier_name,
                        COUNT(*) AS total,
                        SUM(CAST(was_successful AS INTEGER)) AS successful,
                        ROUND(100.0 * SUM(CAST(was_successful AS INTEGER)) / COUNT(*), 2) AS success_rate_pct,
                        AVG(confidence_score) AS avg_confidence
                    FROM fact_verification_executions f
                    JOIN dim_tier tier ON f.tier_key = tier.tier_key
                    JOIN dim_time t ON f.time_key = t.time_key
                    WHERE t.timestamp >= datetime('now', '-' || :days || ' days')
                    GROUP BY tier.tier_name
                """), {"days": days})
            
            return [
                {
                    "tier_name": row[0],
                    "total": row[1],
                    "successful": row[2],
                    "success_rate_pct": row[3],
                    "avg_confidence": round(row[4], 3) if row[4] else None
                }
                for row in result.fetchall()
            ]
    
    async def get_mission_performance(
        self,
        mission_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get mission completion metrics"""
        
        async with async_session() as session:
            if mission_type:
                result = await session.execute(text("""
                    SELECT 
                        m.mission_type,
                        tier.tier_name,
                        COUNT(DISTINCT m.mission_id) AS total_missions,
                        COUNT(DISTINCT CASE WHEN m.final_status = 'success' THEN m.mission_id END) AS successful_missions,
                        AVG(f.confidence_score) AS avg_confidence
                    FROM dim_mission m
                    JOIN fact_verification_executions f ON m.mission_key = f.mission_key
                    JOIN dim_tier tier ON f.tier_key = tier.tier_key
                    WHERE m.mission_type = :mission_type
                    GROUP BY m.mission_type, tier.tier_name
                """), {"mission_type": mission_type})
            else:
                result = await session.execute(text("""
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
                """))
            
            return [
                {
                    "mission_type": row[0],
                    "tier_name": row[1],
                    "total_missions": row[2],
                    "successful_missions": row[3],
                    "success_rate_pct": round(100.0 * row[3] / row[2], 2) if row[2] > 0 else 0,
                    "avg_confidence": round(row[4], 3) if row[4] else None
                }
                for row in result.fetchall()
            ]
    
    async def get_error_trends(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get error event trends over time"""
        
        async with async_session() as session:
            result = await session.execute(text("""
                SELECT 
                    t.year,
                    t.month,
                    t.day,
                    e.severity,
                    COUNT(*) AS error_count,
                    SUM(CAST(was_auto_resolved AS INTEGER)) AS auto_resolved_count
                FROM fact_error_events e
                JOIN dim_time t ON e.time_key = t.time_key
                WHERE t.timestamp >= datetime('now', '-' || :days || ' days')
                GROUP BY t.year, t.month, t.day, e.severity
                ORDER BY t.year, t.month, t.day
            """), {"days": days})
            
            return [
                {
                    "date": f"{row[0]}-{row[1]:02d}-{row[2]:02d}",
                    "severity": row[3],
                    "error_count": row[4],
                    "auto_resolved_count": row[5],
                    "auto_resolve_rate_pct": round(100.0 * row[5] / row[4], 2) if row[4] > 0 else 0
                }
                for row in result.fetchall()
            ]
    
    async def get_daily_rollup(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get daily verification metrics rollup"""
        
        async with async_session() as session:
            result = await session.execute(text("""
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
                WHERE t.timestamp >= datetime('now', '-' || :days || ' days')
                GROUP BY t.year, t.month, t.day, tier.tier_name
                ORDER BY t.year, t.month, t.day
            """), {"days": days})
            
            return [
                {
                    "date": f"{row[0]}-{row[1]:02d}-{row[2]:02d}",
                    "tier_name": row[3],
                    "total_executions": row[4],
                    "successful_executions": row[5],
                    "success_rate_pct": round(100.0 * row[5] / row[4], 2) if row[4] > 0 else 0,
                    "avg_confidence": round(row[6], 3) if row[6] else None,
                    "avg_duration_seconds": round(row[7], 2) if row[7] else None,
                    "rollbacks": row[8]
                }
                for row in result.fetchall()
            ]


# Singleton
grace_cube = GraceCube()
