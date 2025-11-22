"""
Schema Drift Detector - Continuous Integrity Validation
Compares ORM models against live database schema and auto-heals drift
"""

import asyncio
import logging
from typing import Dict, Any, List
from datetime import datetime
from sqlalchemy import text

from backend.models.base_models import engine, Base
from backend.logging_system.immutable_log import immutable_log

logger = logging.getLogger(__name__)


class SchemaDriftDetector:
    """
    Detects and heals schema drift between ORM models and live database

    Features:
    - Periodic schema comparison
    - Auto-healing with extend_existing=True
    - Mission creation for complex fixes
    - Integration with Guardian triggers
    """

    def __init__(self):
        self.check_interval = 300  # 5 minutes
        self.is_running = False
        self.last_check = None
        self.drift_history: List[Dict[str, Any]] = []

    async def start(self):
        """Start periodic schema drift detection"""
        if self.is_running:
            return

        self.is_running = True
        logger.info("[SCHEMA-DRIFT] Starting periodic schema validation")

        # Initial check
        await self.check_schema_drift()

        # Start background task
        asyncio.create_task(self._periodic_check())

    async def stop(self):
        """Stop periodic checking"""
        self.is_running = False
        logger.info("[SCHEMA-DRIFT] Stopped")

    async def _periodic_check(self):
        """Background task for periodic schema checking"""
        while self.is_running:
            try:
                await asyncio.sleep(self.check_interval)
                await self.check_schema_drift()
            except Exception as e:
                logger.error(f"[SCHEMA-DRIFT] Periodic check failed: {e}")

    async def check_schema_drift(self) -> Dict[str, Any]:
        """
        Check for schema drift between ORM models and database

        Returns:
            {
                "drift_detected": bool,
                "missing_tables": List[str],
                "extra_tables": List[str],
                "table_differences": Dict[str, Dict],
                "auto_healed": List[str],
                "needs_manual_fix": List[str]
            }
        """
        logger.info("[SCHEMA-DRIFT] Checking schema integrity")

        try:
            async with engine.begin() as conn:
                # Get database schema
                db_tables = await self._get_database_tables(conn)
                db_columns = await self._get_database_columns(conn)

                # Get ORM schema
                orm_tables = self._get_orm_tables()
                orm_columns = self._get_orm_columns()

                # Compare schemas
                drift_report = self._compare_schemas(
                    db_tables, db_columns, orm_tables, orm_columns
                )

                # Auto-heal what we can
                healed = await self._auto_heal_drift(drift_report, conn)

                # Record results
                self.last_check = datetime.utcnow()
                result = {
                    "timestamp": self.last_check.isoformat(),
                    "drift_detected": len(drift_report["issues"]) > 0,
                    "missing_tables": drift_report["missing_tables"],
                    "extra_tables": drift_report["extra_tables"],
                    "table_differences": drift_report["table_differences"],
                    "auto_healed": healed,
                    "needs_manual_fix": drift_report["needs_manual_fix"]
                }

                self.drift_history.append(result)

                # Log to immutable log
                await immutable_log.append(
                    actor="schema_drift_detector",
                    action="schema_check",
                    resource="database_schema",
                    outcome="completed",
                    payload=result
                )

                # Trigger remediation if needed
                if result["drift_detected"]:
                    await self._trigger_remediation(result)

                logger.info(f"[SCHEMA-DRIFT] Check complete - drift: {result['drift_detected']}")
                return result

        except Exception as e:
            logger.error(f"[SCHEMA-DRIFT] Schema check failed: {e}")
            return {"error": str(e)}

    async def _get_database_tables(self, conn) -> List[str]:
        """Get all tables from database"""
        result = await conn.execute(text("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_type = 'BASE TABLE'
        """))
        return [row[0] for row in result]

    async def _get_database_columns(self, conn) -> Dict[str, List[str]]:
        """Get columns for each table"""
        result = await conn.execute(text("""
            SELECT table_name, column_name
            FROM information_schema.columns
            WHERE table_schema = 'public'
            ORDER BY table_name, ordinal_position
        """))

        columns = {}
        for table_name, column_name in result:
            if table_name not in columns:
                columns[table_name] = []
            columns[table_name].append(column_name)

        return columns

    def _get_orm_tables(self) -> List[str]:
        """Get all tables from ORM models"""
        return [table.name for table in Base.metadata.tables.values()]

    def _get_orm_columns(self) -> Dict[str, List[str]]:
        """Get columns for each ORM table"""
        columns = {}
        for table in Base.metadata.tables.values():
            table_name = table.name
            columns[table_name] = [col.name for col in table.columns]
        return columns

    def _compare_schemas(self, db_tables, db_columns, orm_tables, orm_columns) -> Dict[str, Any]:
        """Compare database vs ORM schemas"""
        missing_tables = [t for t in orm_tables if t not in db_tables]
        extra_tables = [t for t in db_tables if t not in orm_tables and not t.startswith('sqlite_')]

        table_differences = {}
        needs_manual_fix = []

        for table in orm_tables:
            if table in db_columns:
                orm_cols = set(orm_columns.get(table, []))
                db_cols = set(db_columns.get(table, []))

                missing_cols = orm_cols - db_cols
                extra_cols = db_cols - orm_cols

                if missing_cols or extra_cols:
                    table_differences[table] = {
                        "missing_columns": list(missing_cols),
                        "extra_columns": list(extra_cols)
                    }

                    # Check if this needs manual intervention
                    if extra_cols:
                        needs_manual_fix.append(f"Table {table} has extra columns: {extra_cols}")

        return {
            "missing_tables": missing_tables,
            "extra_tables": extra_tables,
            "table_differences": table_differences,
            "needs_manual_fix": needs_manual_fix,
            "issues": missing_tables + extra_tables + list(table_differences.keys())
        }

    async def _auto_heal_drift(self, drift_report: Dict, conn) -> List[str]:
        """Auto-heal schema drift where possible"""
        healed = []

        try:
            # Create missing tables
            for table_name in drift_report["missing_tables"]:
                if table_name in Base.metadata.tables:
                    table = Base.metadata.tables[table_name]
                    logger.info(f"[SCHEMA-DRIFT] Creating missing table: {table_name}")

                    # Create table with extend_existing=True to handle conflicts
                    table.create(bind=conn, checkfirst=True)
                    healed.append(f"Created table {table_name}")

            # Add missing columns
            for table_name, diff in drift_report["table_differences"].items():
                if diff["missing_columns"] and table_name in Base.metadata.tables:
                    table = Base.metadata.tables[table_name]

                    for col_name in diff["missing_columns"]:
                        if col_name in table.columns:
                            column = table.columns[col_name]
                            logger.info(f"[SCHEMA-DRIFT] Adding missing column {col_name} to {table_name}")

                            # Add column
                            alter_sql = f"ALTER TABLE {table_name} ADD COLUMN {col_name} {self._get_column_type(column)}"
                            await conn.execute(text(alter_sql))
                            healed.append(f"Added column {col_name} to {table_name}")

        except Exception as e:
            logger.error(f"[SCHEMA-DRIFT] Auto-healing failed: {e}")

        return healed

    def _get_column_type(self, column) -> str:
        """Get SQL type string for column"""
        # This is a simplified version - in production you'd map SQLAlchemy types properly
        type_name = str(column.type).upper()
        if "VARCHAR" in type_name:
            return type_name
        elif "INTEGER" in type_name:
            return "INTEGER"
        elif "TEXT" in type_name:
            return "TEXT"
        elif "BOOLEAN" in type_name:
            return "BOOLEAN"
        elif "FLOAT" in type_name:
            return "FLOAT"
        else:
            return "TEXT"  # Default fallback

    async def _trigger_remediation(self, drift_report: Dict):
        """Trigger remediation missions for schema drift"""
        try:
            from backend.autonomy.proactive_mission_generator import proactive_mission_generator

            # Create mission for manual fixes needed
            if drift_report.get("needs_manual_fix"):
                issues_text = "\\n".join(drift_report["needs_manual_fix"])

                await proactive_mission_generator.create_mission(
                    title="Schema Drift Remediation Required",
                    description=f"Database schema drift detected that requires manual intervention:\\n{issues_text}",
                    priority="high",
                    mission_type="infrastructure",
                    context={
                        "drift_report": drift_report,
                        "triggered_by": "schema_drift_detector"
                    }
                )

        except Exception as e:
            logger.error(f"[SCHEMA-DRIFT] Failed to trigger remediation: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Get detector statistics"""
        total_checks = len(self.drift_history)
        drift_detected = sum(1 for h in self.drift_history if h.get("drift_detected"))

        return {
            "total_checks": total_checks,
            "drift_detected": drift_detected,
            "drift_rate": drift_detected / total_checks if total_checks > 0 else 0,
            "last_check": self.last_check.isoformat() if self.last_check else None,
            "is_running": self.is_running,
            "check_interval_seconds": self.check_interval
        }


# Global instance
schema_drift_detector = SchemaDriftDetector()
