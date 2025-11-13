"""
Setup initial self-healing data for testing
"""
import asyncio
from datetime import datetime, timezone
from backend.memory_tables.registry import table_registry

async def setup_self_healing_data():
    """Add sample self-healing data"""
    
    # Sample playbooks
    playbooks = [
        {
            "playbook_name": "Restart Failed Service",
            "description": "Automatically restart a failed service component",
            "target_components": ["reflection_service", "task_executor"],
            "risk_level": "low",
            "status": "active",
            "created_at": datetime.now().isoformat(),
            "execution_stats": {"total_runs": 15, "successful_runs": 14, "last_run": "2024-01-15T10:30:00Z"}
        },
        {
            "playbook_name": "Database Connection Recovery",
            "description": "Recover from database connection failures",
            "target_components": ["database"],
            "risk_level": "medium",
            "status": "active",
            "created_at": datetime.now().isoformat(),
            "execution_stats": {"total_runs": 8, "successful_runs": 7, "last_run": "2024-01-15T09:15:00Z"}
        },
        {
            "playbook_name": "Memory Cleanup",
            "description": "Clean up memory when usage exceeds threshold",
            "target_components": ["system"],
            "risk_level": "high",
            "status": "pending_approval",
            "created_at": datetime.now().isoformat(),
            "execution_stats": {"total_runs": 0, "successful_runs": 0}
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
    
    print("🔧 Setting up self-healing data...")
    
    # Insert data
    for playbook in playbooks:
        await table_registry.insert_row("memory_self_healing_playbooks", playbook)
    print(f"✅ Added {len(playbooks)} playbooks")
    
    for log in execution_logs:
        await table_registry.insert_row("memory_execution_logs", log)
    print(f"✅ Added {len(execution_logs)} execution logs")
    
    for incident in incidents:
        await table_registry.insert_row("memory_incidents", incident)
    print(f"✅ Added {len(incidents)} incidents")
    
    for agent in agents:
        await table_registry.insert_row("memory_sub_agents", agent)
    print(f"✅ Added {len(agents)} agents")
    
    for insight in insights:
        await table_registry.insert_row("memory_insights", insight)
    print(f"✅ Added {len(insights)} insights")
    
    print("🚀 Self-healing data setup complete!")

if __name__ == "__main__":
    asyncio.run(setup_self_healing_data())