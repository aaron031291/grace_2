"""
Setup initial self-healing data for testing
"""
import asyncio
import sys
import os
from datetime import datetime, timezone
from pathlib import Path

# Add backend to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from memory_tables.registry import table_registry

async def setup_self_healing_data():
    """Add sample self-healing data"""

    # Initialize memory tables first
    from memory_tables.registry import table_registry
    from memory_tables.initialization import initialize_memory_tables

    # Fix schema directory path since we're running from backend/
    table_registry.schema_dir = Path("memory_tables/schema")

    tables_initialized = await initialize_memory_tables()
    if not tables_initialized:
        print("Failed to initialize memory tables")
        return

    # Sample playbooks with proper structure
    playbooks = [
        {
            "playbook_name": "Restart Failed Service",
            "description": "Automatically restart a failed service component",
            "trigger_conditions": [
                {"type": "event_type", "value": "service.crashed"},
                {"type": "component", "value": "reflection_service"},
                {"type": "component", "value": "task_executor"}
            ],
            "actions": [
                {
                    "name": "Stop service",
                    "action": "restart_service",
                    "args": {"service_name": "{{component}}"},
                    "success_criteria": {"result_contains": "restarted"}
                },
                {
                    "name": "Verify service health",
                    "action": "run_verification",
                    "args": {"check_type": "service_health"},
                    "success_criteria": {"result_equals": True}
                }
            ],
            "target_components": ["reflection_service", "task_executor"],
            "risk_level": "low",
            "requires_approval": False,
            "total_runs": 15,
            "successful_runs": 14,
            "success_rate": 0.93,
            "trust_score": 0.85,
            "last_used_at": "2024-01-15T10:30:00Z"
        },
        {
            "playbook_name": "Database Connection Recovery",
            "description": "Recover from database connection failures",
            "trigger_conditions": [
                {"type": "event_type", "value": "database.connection_failed"},
                {"type": "error_type", "value": "ConnectionError"}
            ],
            "actions": [
                {
                    "name": "Test connection",
                    "action": "run_verification",
                    "args": {"check_type": "database_connection"},
                    "success_criteria": {"result_equals": True}
                },
                {
                    "name": "Switch to read-only mode",
                    "action": "update_config",
                    "args": {"key": "database_mode", "value": "read_only"},
                    "success_criteria": {"result_contains": "updated"}
                }
            ],
            "target_components": ["database"],
            "risk_level": "medium",
            "requires_approval": False,
            "total_runs": 8,
            "successful_runs": 7,
            "success_rate": 0.88,
            "trust_score": 0.82,
            "last_used_at": "2024-01-15T09:15:00Z"
        },
        {
            "playbook_name": "Ingestion Failure Recovery",
            "description": "Recover from ingestion pipeline failures",
            "trigger_conditions": [
                {"type": "event_type", "value": "ingestion.failed"},
                {"type": "event_type", "value": "pipeline.timeout"}
            ],
            "actions": [
                {
                    "name": "Clear ingestion cache",
                    "action": "clear_cache",
                    "args": {"cache_type": "ingestion"},
                    "success_criteria": {"result_contains": "cleared"}
                },
                {
                    "name": "Rerun ingestion",
                    "action": "rerun_ingestion",
                    "args": {"source": "{{source}}"},
                    "success_criteria": {"result_equals": True}
                },
                {
                    "name": "Run verification",
                    "action": "run_verification",
                    "args": {"check_type": "ingestion_verification"},
                    "success_criteria": {"result_equals": True}
                }
            ],
            "target_components": ["ingestion_pipeline"],
            "risk_level": "medium",
            "requires_approval": False,
            "total_runs": 5,
            "successful_runs": 4,
            "success_rate": 0.8,
            "trust_score": 0.75,
            "last_used_at": "2024-01-15T11:00:00Z"
        },
        {
            "playbook_name": "Schema Validation Recovery",
            "description": "Recover from schema validation failures",
            "trigger_conditions": [
                {"type": "event_type", "value": "schema.invalid"},
                {"type": "event_type", "value": "verification.failed"}
            ],
            "actions": [
                {
                    "name": "Validate schema",
                    "action": "run_verification",
                    "args": {"check_type": "schema_validation"},
                    "success_criteria": {"result_equals": True}
                },
                {
                    "name": "Send notification",
                    "action": "send_notification",
                    "args": {"message": "Schema validation failed - manual intervention required"},
                    "success_criteria": {"result_contains": "sent"}
                }
            ],
            "target_components": ["schema_validator"],
            "risk_level": "high",
            "requires_approval": True,
            "total_runs": 2,
            "successful_runs": 1,
            "success_rate": 0.5,
            "trust_score": 0.45,
            "last_used_at": "2024-01-15T12:00:00Z"
        }
    ]
    
    # Sample execution logs
    execution_logs = [
        {
            "playbook_id": "1",
            "playbook_name": "Restart Failed Service",
            "started_at": "2024-01-15T10:30:00Z",
            "completed_at": "2024-01-15T10:30:15Z",
            "status": "success",
            "triggered_by": "automatic",
            "duration_ms": 15000,
            "result": "Service restarted successfully"
        },
        {
            "playbook_id": "2",
            "playbook_name": "Database Connection Recovery",
            "started_at": "2024-01-15T09:15:00Z",
            "completed_at": "2024-01-15T09:15:30Z",
            "status": "success",
            "triggered_by": "automatic",
            "duration_ms": 30000,
            "result": "Database connection restored"
        }
    ]
    
    # Sample incidents
    incidents = [
        {
            "title": "High Memory Usage Detected",
            "description": "System memory usage exceeded 85% threshold",
            "severity": "medium",
            "status": "open",
            "created_at": datetime.now().isoformat(),
            "affected_components": ["system"]
        }
    ]
    
    # Sample agents
    agents = [
        {
            "name": "Memory Monitor",
            "description": "Monitors system memory usage",
            "domain": "self_healing",
            "status": "active",
            "created_at": datetime.now().isoformat(),
            "capabilities": ["monitor_memory", "trigger_cleanup"]
        },
        {
            "name": "Service Watchdog",
            "description": "Monitors service health and restarts failed services",
            "domain": "self_healing", 
            "status": "active",
            "created_at": datetime.now().isoformat(),
            "capabilities": ["monitor_services", "restart_services"]
        }
    ]
    
    # Sample insights
    insights = [
        {
            "title": "Pattern Detected: Service Failures",
            "description": "Reflection service tends to fail during high load periods",
            "domain": "self_healing",
            "confidence": 0.85,
            "created_at": datetime.now().isoformat(),
            "insight_type": "pattern_detection"
        },
        {
            "title": "Optimization Opportunity",
            "description": "Database connection pooling could reduce recovery time",
            "domain": "self_healing",
            "confidence": 0.75,
            "created_at": datetime.now().isoformat(),
            "insight_type": "optimization"
        }
    ]
    
    print("Setting up self-healing data...")
    
    # Insert data (use synchronous insert_row)
    for playbook in playbooks:
        table_registry.insert_row("memory_self_healing_playbooks", playbook)
    print(f"Added {len(playbooks)} playbooks")

    for log in execution_logs:
        table_registry.insert_row("memory_execution_logs", log)
    print(f"Added {len(execution_logs)} execution logs")

    for incident in incidents:
        table_registry.insert_row("memory_incidents", incident)
    print(f"Added {len(incidents)} incidents")

    for agent in agents:
        table_registry.insert_row("memory_sub_agents", agent)
    print(f"Added {len(agents)} agents")

    for insight in insights:
        table_registry.insert_row("memory_insights", insight)
    print(f"Added {len(insights)} insights")

    print("Self-healing data setup complete!")

if __name__ == "__main__":
    asyncio.run(setup_self_healing_data())