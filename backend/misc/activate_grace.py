"""
GRACE Autonomy Activation Script

Quick starter to activate GRACE's agentic spine with example playbooks,
health nodes, and compliance rules.
"""

import asyncio
from datetime import datetime

from .grace_spine_integration import activate_grace_autonomy, grace_agentic_system
from .agentic_spine import agentic_spine, Playbook, RiskLevel, HealthNode
from .ethics_sentinel import ethics_sentinel, ComplianceRule, SeverityLevel
from .meta_loop_supervisor import meta_loop_supervisor
from .proactive_intelligence import proactive_intelligence


async def register_example_playbooks():
    """Register example recovery playbooks"""
    
    print("\n📚 Registering example playbooks...")
    
    restart_playbook = Playbook(
        playbook_id="restart_degraded_service",
        name="Restart Degraded Service",
        description="Restart service when health checks fail",
        preconditions=[
            {"condition": "health_check_failing", "value": True}
        ],
        steps=[
            {"action": "drain_traffic", "description": "Remove service from load balancer"},
            {"action": "restart_service", "description": "Restart the service process"},
            {"action": "wait_for_healthy", "duration_seconds": 30},
            {"action": "restore_traffic", "description": "Add service back to load balancer"}
        ],
        verifications=[
            {"check": "health_endpoint_responding"},
            {"check": "error_rate_below_threshold", "threshold": 0.01}
        ],
        rollback_steps=[
            {"action": "rollback_to_previous_version"}
        ],
        risk_level=RiskLevel.LOW,
        requires_approval=False,
        success_rate=0.92,
        execution_count=150
    )
    await agentic_spine.planner.register_playbook(restart_playbook)
    
    scale_up_playbook = Playbook(
        playbook_id="scale_up_on_load",
        name="Scale Up Service Under Load",
        description="Add capacity when service is overloaded",
        preconditions=[
            {"condition": "cpu_utilization_high", "threshold": 80},
            {"condition": "current_capacity", "operator": "less_than", "value": "max_capacity"}
        ],
        steps=[
            {"action": "calculate_target_capacity"},
            {"action": "provision_instances", "scale_factor": 1.5},
            {"action": "wait_for_instances_ready", "timeout_seconds": 120},
            {"action": "add_to_load_balancer"}
        ],
        verifications=[
            {"check": "cpu_utilization_normalized", "threshold": 60},
            {"check": "all_instances_healthy"}
        ],
        rollback_steps=[
            {"action": "terminate_new_instances"}
        ],
        risk_level=RiskLevel.MODERATE,
        requires_approval=False,
        success_rate=0.87,
        execution_count=89
    )
    await agentic_spine.planner.register_playbook(scale_up_playbook)
    
    database_failover = Playbook(
        playbook_id="database_failover",
        name="Database Failover to Replica",
        description="Failover to database replica when primary fails",
        preconditions=[
            {"condition": "primary_db_unreachable", "value": True},
            {"condition": "replica_lag", "operator": "less_than", "value": 5}
        ],
        steps=[
            {"action": "verify_replica_health"},
            {"action": "promote_replica_to_primary"},
            {"action": "update_connection_strings"},
            {"action": "restart_app_servers"}
        ],
        verifications=[
            {"check": "database_writable"},
            {"check": "application_healthy"}
        ],
        rollback_steps=[
            {"action": "restore_original_primary"},
            {"action": "revert_connection_strings"}
        ],
        risk_level=RiskLevel.HIGH,
        requires_approval=True,
        success_rate=0.95,
        execution_count=12
    )
    await agentic_spine.planner.register_playbook(database_failover)
    
    print("  ✓ Registered 3 playbooks")


async def register_example_health_nodes():
    """Register example health nodes in the unified graph"""
    
    print("\n🏥 Registering health nodes...")
    
    api_service = HealthNode(
        node_id="api-service",
        node_type="service",
        name="API Service",
        status="healthy",
        kpis={
            "latency_p95": 180,
            "latency_p99": 450,
            "error_rate": 0.005,
            "request_rate": 1500
        },
        dependencies=["database-primary", "cache-cluster", "auth-service"],
        dependents=["web-frontend", "mobile-app"],
        blast_radius=0,
        priority=0
    )
    await agentic_spine.health_graph.register_node(api_service)
    
    database = HealthNode(
        node_id="database-primary",
        node_type="database",
        name="Primary Database",
        status="healthy",
        kpis={
            "connection_pool_usage": 45,
            "query_latency_avg": 12,
            "replication_lag": 0
        },
        dependencies=[],
        dependents=["api-service", "worker-service"],
        blast_radius=0,
        priority=0
    )
    await agentic_spine.health_graph.register_node(database)
    
    cache = HealthNode(
        node_id="cache-cluster",
        node_type="cache",
        name="Redis Cache Cluster",
        status="healthy",
        kpis={
            "hit_rate": 0.92,
            "memory_usage": 68,
            "connected_clients": 45
        },
        dependencies=[],
        dependents=["api-service"],
        blast_radius=0,
        priority=0
    )
    await agentic_spine.health_graph.register_node(cache)
    
    frontend = HealthNode(
        node_id="web-frontend",
        node_type="service",
        name="Web Frontend",
        status="healthy",
        kpis={
            "render_time_p95": 850,
            "error_rate": 0.002
        },
        dependencies=["api-service", "cdn"],
        dependents=[],
        blast_radius=0,
        priority=0
    )
    await agentic_spine.health_graph.register_node(frontend)
    
    print("  ✓ Registered 4 health nodes")


async def register_example_compliance_rules():
    """Register example compliance rules"""
    
    print("\n⚖️  Registering compliance rules...")
    
    no_prod_deletes = ComplianceRule(
        rule_id="no_production_data_deletion",
        rule_type="data_protection",
        description="Prevent production data deletion without approval",
        pattern={
            "action": "delete",
            "context_conditions": {
                "environment": "production"
            }
        },
        severity=SeverityLevel.BLOCKING,
        requires_human_review=True,
        auto_block=True
    )
    await ethics_sentinel.policy_monitor.register_rule(no_prod_deletes)
    
    prod_deploy_approval = ComplianceRule(
        rule_id="production_deploy_approval",
        rule_type="change_management",
        description="Production deployments require approval",
        pattern={
            "action": "deploy",
            "context_conditions": {
                "environment": "production"
            }
        },
        severity=SeverityLevel.WARNING,
        requires_human_review=True,
        auto_block=False
    )
    await ethics_sentinel.policy_monitor.register_rule(prod_deploy_approval)
    
    high_cost_approval = ComplianceRule(
        rule_id="high_cost_action_approval",
        rule_type="cost_control",
        description="High-cost actions require approval",
        pattern={
            "context_conditions": {
                "estimated_cost_threshold": 1000
            }
        },
        severity=SeverityLevel.WARNING,
        requires_human_review=True,
        auto_block=False
    )
    await ethics_sentinel.policy_monitor.register_rule(high_cost_approval)
    
    print("  ✓ Registered 3 compliance rules")


async def main():
    """Main activation sequence"""
    
    print("\n" + "=" * 70)
    print(" GRACE AUTONOMY ACTIVATION")
    print("=" * 70)
    
    await activate_grace_autonomy()
    
    await register_example_playbooks()
    await register_example_health_nodes()
    await register_example_compliance_rules()
    
    print("\n" + "=" * 70)
    print(" GRACE IS NOW FULLY AUTONOMOUS")
    print("=" * 70)
    
    status = await grace_agentic_system.get_status()
    print(f"\n✅ System Status: {status['health']['status']}")
    print(f"✅ Active Systems: {len([s for s in status['health']['systems'].values() if s == 'running'])}")
    print(f"✅ Capabilities: {len(status['capabilities'])}")
    
    print("\n📊 Meta Loop Supervisor:")
    print(f"  • Monitoring {len(await meta_loop_supervisor.snapshot_builder._get_active_domains())} domains")
    print(f"  • Running {len(meta_loop_supervisor.strategy_engine.policies)} meta policies")
    print(f"  • Cycle interval: {meta_loop_supervisor.cycle_interval_seconds}s")
    
    print("\n🔮 Proactive Intelligence:")
    print(f"  • Anomaly forecasting: 30-60min ahead")
    print(f"  • Capacity prediction: Active")
    print(f"  • Risk assessment: Continuous")
    print(f"  • Drift detection: Real-time")
    print(f"  • Prediction cycle: Every {proactive_intelligence.prediction_interval_seconds}s")
    
    print("\n" + "=" * 70)
    print(" MONITORING (Ctrl+C to stop)")
    print("=" * 70)
    
    try:
        iteration = 0
        while True:
            await asyncio.sleep(30)
            iteration += 1
            
            if iteration % 2 == 0:
                health = await grace_agentic_system.health_check()
                uptime = health['uptime_seconds']
                uptime_mins = int(uptime // 60)
                print(f"\n[{datetime.utcnow().strftime('%H:%M:%S')}] Health Check - Uptime: {uptime_mins}m - Status: {health['status']}")
            
            if iteration % 120 == 0:
                compliance = await ethics_sentinel.dashboard.generate_compliance_report()
                print(f"\n[Compliance] Score: {compliance['compliance_score']:.1f}/100 - Violations (7d): {compliance['violations']['last_7_days']}")
    
    except KeyboardInterrupt:
        print("\n\n🛑 Shutdown signal received...")
        from .grace_spine_integration import deactivate_grace_autonomy
        await deactivate_grace_autonomy()
        print("\n✅ GRACE autonomy deactivated gracefully")


if __name__ == "__main__":
    asyncio.run(main())
