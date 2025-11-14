"""
Kernel Management API
Provides kernel status, actions, config, and log streaming per layer
"""
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
import asyncio

router = APIRouter(prefix="/api/kernels", tags=["kernels"])


class KernelAction(BaseModel):
    action: str
    params: Optional[Dict[str, Any]] = None


class KernelConfig(BaseModel):
    config: Dict[str, Any]


# ========== LAYER 1: CORE EXECUTION KERNELS ==========

@router.get("/layer1/status")
async def get_layer1_kernels():
    """
    Get status of all Layer 1 core execution kernels
    Memory, Librarian, Governance, Verification, Self-Healing, Ingestion, Crypto
    """
    kernels = [
        {
            "kernel_id": "memory-kernel-01",
            "name": "Memory Kernel",
            "type": "memory",
            "status": "active",
            "uptime_seconds": 12300,
            "current_tasks": 45,
            "health": "healthy",
            "metrics": {
                "memory_usage_mb": 2300,
                "memory_limit_mb": 8000,
                "cpu_percent": 35,
                "tables_count": 87,
                "cache_hit_rate": 0.92
            },
            "last_action": "Indexed 1,234 entries",
            "quick_actions": ["flush_cache", "rebuild_index", "export_stats", "run_diagnostics"],
            "config_options": [
                {"name": "max_memory_gb", "type": "slider", "value": 8, "min": 2, "max": 32, "label": "Max Memory (GB)"},
                {"name": "max_tables", "type": "slider", "value": 100, "min": 10, "max": 1000, "label": "Max Tables"},
                {"name": "auto_optimize", "type": "toggle", "value": True, "label": "Auto-optimize"},
                {"name": "log_level", "type": "dropdown", "value": "INFO", "options": ["DEBUG", "INFO", "WARN", "ERROR"], "label": "Log Level"}
            ]
        },
        {
            "kernel_id": "librarian-kernel-01",
            "name": "Librarian Kernel",
            "type": "librarian",
            "status": "active",
            "uptime_seconds": 8100,
            "current_tasks": 3,
            "health": "healthy",
            "metrics": {
                "books_processed": 156,
                "current_file": "book_qa.pdf",
                "queue_depth": 5
            },
            "last_action": "Processing: book_qa.pdf",
            "quick_actions": ["pause_processing", "view_queue", "export_analysis", "clear_completed"],
            "config_options": [
                {"name": "max_concurrent", "type": "slider", "value": 3, "min": 1, "max": 10, "label": "Max Concurrent Books"},
                {"name": "auto_analyze", "type": "toggle", "value": True, "label": "Auto-analyze"},
                {"name": "extract_images", "type": "toggle", "value": True, "label": "Extract Images"}
            ]
        },
        {
            "kernel_id": "governance-kernel-01",
            "name": "Governance Kernel",
            "type": "governance",
            "status": "paused",
            "uptime_seconds": 15600,
            "current_tasks": 0,
            "health": "healthy",
            "metrics": {
                "active_sessions": 0,
                "pending_approvals": 2,
                "total_votes_today": 12
            },
            "last_action": "Paused by user",
            "quick_actions": ["view_pending_approvals", "create_session", "view_constitution", "export_audit"],
            "config_options": [
                {"name": "quorum_required", "type": "slider", "value": 3, "min": 1, "max": 10, "label": "Quorum Required"},
                {"name": "strict_mode", "type": "toggle", "value": True, "label": "Strict Mode"}
            ]
        },
        {
            "kernel_id": "verification-kernel-01",
            "name": "Verification Kernel",
            "type": "verification",
            "status": "active",
            "uptime_seconds": 18900,
            "current_tasks": 23,
            "health": "healthy",
            "metrics": {
                "verifications_today": 456,
                "failures_today": 3,
                "success_rate": 0.993
            },
            "quick_actions": ["verify_all", "rebuild_trust", "export_failures", "clear_cache"]
        },
        {
            "kernel_id": "self-heal-kernel-01",
            "name": "Self-Healing Kernel",
            "type": "self_heal",
            "status": "active",
            "uptime_seconds": 21600,
            "current_tasks": 0,
            "health": "healthy",
            "metrics": {
                "anomalies_detected_today": 5,
                "auto_fixes_applied": 5,
                "success_rate": 1.0
            },
            "quick_actions": ["run_health_check", "view_anomalies", "disable_auto_heal", "export_report"]
        },
        {
            "kernel_id": "ingestion-kernel-01",
            "name": "Ingestion Kernel",
            "type": "ingestion",
            "status": "active",
            "uptime_seconds": 25200,
            "current_tasks": 8,
            "health": "healthy",
            "metrics": {
                "files_processed_today": 234,
                "queue_depth": 12,
                "throughput_mb_per_hour": 85.36
            },
            "quick_actions": ["pause_ingestion", "retry_failed", "export_stats", "clear_queue"]
        },
        {
            "kernel_id": "crypto-kernel-01",
            "name": "Crypto Kernel",
            "type": "crypto",
            "status": "active",
            "uptime_seconds": 28800,
            "current_tasks": 0,
            "health": "healthy",
            "metrics": {
                "signatures_validated": 1234,
                "signature_failures": 2,
                "encrypted_items": 456,
                "key_rotation_due_days": 5
            },
            "quick_actions": ["rotate_keys", "backup_keys", "validate_all", "export_audit"]
        }
    ]
    
    return {"kernels": kernels}


# ========== LAYER 2: HTM/SCHEDULER KERNELS ==========

@router.get("/layer2/status")
async def get_layer2_kernels():
    """
    Get status of all Layer 2 HTM and scheduler kernels
    HTM Queue, Trigger Engine, Scheduler, Agent Pool, Task Router
    """
    kernels = [
        {
            "kernel_id": "htm-queue-01",
            "name": "HTM Queue Manager",
            "type": "htm_queue",
            "status": "active",
            "uptime_seconds": 18000,
            "current_tasks": 145,
            "health": "healthy",
            "metrics": {
                "queue_depth": 145,
                "pending_tasks": 85,
                "active_tasks": 60,
                "sla_breaches": 2,
                "avg_wait_time_seconds": 45,
                "p95_duration_seconds": 120
            },
            "quick_actions": ["pause_queue", "flush_completed", "spawn_agent", "export_queue"],
            "config_options": [
                {"name": "max_queue_depth", "type": "slider", "value": 500, "min": 50, "max": 5000, "label": "Max Queue Depth"},
                {"name": "sla_max_wait", "type": "slider", "value": 60, "min": 10, "max": 300, "label": "SLA Max Wait (s)"},
                {"name": "sla_max_duration", "type": "slider", "value": 120, "min": 30, "max": 600, "label": "SLA Max Duration (s)"}
            ]
        },
        {
            "kernel_id": "trigger-engine-01",
            "name": "Trigger Engine",
            "type": "trigger",
            "status": "active",
            "uptime_seconds": 21600,
            "current_tasks": 0,
            "health": "healthy",
            "metrics": {
                "active_triggers": 23,
                "triggers_fired_today": 156,
                "failed_triggers": 2
            },
            "quick_actions": ["add_trigger", "disable_all", "view_history", "export_rules"]
        },
        {
            "kernel_id": "scheduler-kernel-01",
            "name": "Scheduler Kernel",
            "type": "scheduler",
            "status": "active",
            "uptime_seconds": 28800,
            "current_tasks": 3,
            "health": "healthy",
            "metrics": {
                "scheduled_jobs": 45,
                "executed_today": 234,
                "missed_jobs": 0
            },
            "quick_actions": ["run_now", "pause_all", "view_upcoming", "export_schedule"]
        },
        {
            "kernel_id": "agent-pool-01",
            "name": "Agent Pool Manager",
            "type": "agent_pool",
            "status": "active",
            "uptime_seconds": 32400,
            "current_tasks": 7,
            "health": "healthy",
            "metrics": {
                "active_agents": 7,
                "idle_agents": 2,
                "capacity_utilization": 0.78
            },
            "quick_actions": ["spawn_agent", "terminate_idle", "balance_load", "export_metrics"]
        },
        {
            "kernel_id": "task-router-01",
            "name": "Task Router",
            "type": "task_router",
            "status": "active",
            "uptime_seconds": 36000,
            "current_tasks": 12,
            "health": "healthy",
            "metrics": {
                "tasks_routed_today": 567,
                "routing_failures": 1
            },
            "quick_actions": ["view_routes", "add_route", "reset_defaults", "export_rules"]
        }
    ]
    
    return {"kernels": kernels}


# ========== LAYER 3: AGENTIC BRAIN KERNELS ==========

@router.get("/layer3/status")
async def get_layer3_kernels():
    """
    Get status of all Layer 3 agentic brain kernels
    Learning Loop, Intent Engine, Policy AI, Enrichment, Trust Core, Playbook Runtime
    """
    kernels = [
        {
            "kernel_id": "learning-loop-01",
            "name": "Learning Loop",
            "type": "learning",
            "status": "active",
            "uptime_seconds": 43200,
            "current_tasks": 1,
            "health": "healthy",
            "metrics": {
                "current_cycle": 47,
                "insights_count": 12,
                "improvements_count": 5,
                "success_rate_percent": 94.5,
                "last_retrospective": "2025-11-14T08:30:00Z"
            },
            "quick_actions": ["generate_retro", "apply_learning", "view_history", "export_insights"],
            "config_options": [
                {"name": "min_insights", "type": "slider", "value": 5, "min": 1, "max": 20, "label": "Min Insights"},
                {"name": "confidence_min", "type": "slider", "value": 0.8, "min": 0.5, "max": 1.0, "label": "Min Confidence"},
                {"name": "auto_apply", "type": "toggle", "value": True, "label": "Auto-apply High Confidence"}
            ]
        },
        {
            "kernel_id": "intent-engine-01",
            "name": "Intent Engine",
            "type": "intent",
            "status": "active",
            "uptime_seconds": 39600,
            "current_tasks": 3,
            "health": "healthy",
            "metrics": {
                "active_intents": 3,
                "completed_today": 5,
                "avg_completion_time_hours": 2.5
            },
            "quick_actions": ["create_intent", "view_active", "cancel_intent", "export_report"]
        },
        {
            "kernel_id": "policy-ai-01",
            "name": "Policy AI",
            "type": "policy",
            "status": "active",
            "uptime_seconds": 46800,
            "current_tasks": 0,
            "health": "healthy",
            "metrics": {
                "suggestions_pending": 5,
                "suggestions_accepted": 12,
                "avg_confidence": 0.83
            },
            "quick_actions": ["generate_suggestions", "view_pending", "apply_accepted", "export_policies"]
        },
        {
            "kernel_id": "enrichment-kernel-01",
            "name": "Enrichment Engine",
            "type": "enrichment",
            "status": "active",
            "uptime_seconds": 50400,
            "current_tasks": 15,
            "health": "healthy",
            "metrics": {
                "enrichments_today": 789,
                "links_created": 456,
                "external_api_calls": 123
            },
            "quick_actions": ["enrich_now", "rebuild_links", "clear_cache", "export_graph"]
        },
        {
            "kernel_id": "trust-core-01",
            "name": "Trust Core",
            "type": "trust",
            "status": "active",
            "uptime_seconds": 54000,
            "current_tasks": 8,
            "health": "healthy",
            "metrics": {
                "sources_scored": 234,
                "avg_trust_score": 0.85,
                "untrusted_sources": 3
            },
            "quick_actions": ["recalculate_all", "view_untrusted", "reset_scores", "export_report"]
        },
        {
            "kernel_id": "playbook-runtime-01",
            "name": "Playbook Runtime",
            "type": "playbook",
            "status": "active",
            "uptime_seconds": 57600,
            "current_tasks": 2,
            "health": "healthy",
            "metrics": {
                "playbooks_running": 2,
                "executed_today": 45,
                "success_rate": 0.945
            },
            "quick_actions": ["run_playbook", "view_active", "pause_execution", "export_stats"]
        }
    ]
    
    return {"kernels": kernels}


# ========== LAYER 4: DEV/OS SERVICES ==========

@router.get("/layer4/status")
async def get_layer4_services():
    """
    Get status of all Layer 4 dev/OS services
    Secrets Vault, Recording Pipeline, Remote Access, Deployment, Stress Runner, Monitoring
    """
    services = [
        {
            "service_id": "secrets-vault-01",
            "name": "Secrets Vault Service",
            "type": "secrets",
            "status": "active",
            "uptime_seconds": 86400,
            "current_tasks": 0,
            "health": "healthy",
            "metrics": {
                "total_secrets": 15,
                "encrypted_secrets": 15,
                "next_rotation_days": 5,
                "last_audit": "2025-11-14T08:30:00Z"
            },
            "quick_actions": ["add_secret", "rotate_keys", "backup_vault", "view_audit"],
            "config_options": [
                {"name": "encryption_algorithm", "type": "dropdown", "value": "AES-256", "options": ["AES-256", "RSA-4096"], "label": "Encryption"},
                {"name": "auto_rotate", "type": "toggle", "value": True, "label": "Auto-rotate Keys"},
                {"name": "rotation_period_days", "type": "slider", "value": 90, "min": 30, "max": 365, "label": "Rotation Period (days)"}
            ]
        },
        {
            "service_id": "recording-pipeline-01",
            "name": "Recording Pipeline",
            "type": "recording",
            "status": "active",
            "uptime_seconds": 72000,
            "current_tasks": 2,
            "health": "healthy",
            "metrics": {
                "pending_recordings": 5,
                "processing_count": 2,
                "processing_progress_percent": 45,
                "completed_today": 8
            },
            "quick_actions": ["ingest_all", "view_queue", "export_transcripts", "clear_processed"]
        },
        {
            "service_id": "remote-access-01",
            "name": "Remote Access Agent",
            "type": "remote_access",
            "status": "active",
            "uptime_seconds": 64800,
            "current_tasks": 1,
            "health": "healthy",
            "metrics": {
                "active_sessions": 1,
                "sessions_today": 5,
                "total_session_time_minutes": 180
            },
            "quick_actions": ["view_active_sessions", "terminate_session", "export_session_log", "review_commands"]
        },
        {
            "service_id": "deployment-service-01",
            "name": "Deployment Service",
            "type": "deployment",
            "status": "active",
            "uptime_seconds": 7200,
            "current_tasks": 1,
            "health": "healthy",
            "metrics": {
                "current_stage": "testing",
                "progress_percent": 65,
                "last_deployment": "2025-11-12T06:00:00Z",
                "environment": "staging"
            },
            "quick_actions": ["deploy_staging", "promote_production", "rollback", "view_pipeline"]
        },
        {
            "service_id": "stress-runner-01",
            "name": "Stress Test Runner",
            "type": "stress",
            "status": "idle",
            "uptime_seconds": 90000,
            "current_tasks": 0,
            "health": "healthy",
            "metrics": {
                "last_test": "2025-11-13T10:00:00Z",
                "avg_test_duration_minutes": 12,
                "tests_run_this_week": 5
            },
            "quick_actions": ["run_test", "view_results", "export_report", "load_template"]
        },
        {
            "service_id": "monitoring-service-01",
            "name": "Monitoring Service",
            "type": "monitoring",
            "status": "active",
            "uptime_seconds": 93600,
            "current_tasks": 0,
            "health": "healthy",
            "metrics": {
                "active_alerts": 0,
                "metrics_collected_per_min": 120,
                "storage_used_mb": 1200
            },
            "quick_actions": ["run_health_check", "view_alerts", "configure_alerts", "export_metrics"]
        }
    ]
    
    return {"services": services}


# ========== KERNEL ACTIONS ==========

@router.post("/{kernel_id}/action")
async def execute_kernel_action(kernel_id: str, action_data: KernelAction):
    """
    Execute an action on a specific kernel
    Actions: start, stop, restart, pause, resume, or kernel-specific quick actions
    """
    action = action_data.action
    params = action_data.params or {}
    
    # Validate kernel exists (stub - would check database)
    if not kernel_id.startswith(('memory-', 'librarian-', 'htm-', 'secrets-', 'learning-', 'intent-')):
        raise HTTPException(status_code=404, detail="Kernel not found")
    
    # Execute action based on type
    if action == "start":
        result = f"Kernel {kernel_id} started"
    elif action == "stop":
        result = f"Kernel {kernel_id} stopped"
    elif action == "restart":
        result = f"Kernel {kernel_id} restarted"
    elif action == "pause":
        result = f"Kernel {kernel_id} paused"
    elif action == "resume":
        result = f"Kernel {kernel_id} resumed"
    else:
        result = f"Executed {action} on {kernel_id}"
    
    return {
        "kernel_id": kernel_id,
        "action": action,
        "status": "success",
        "message": result,
        "params": params
    }


# ========== KERNEL CONFIG ==========

@router.get("/{kernel_id}/config")
async def get_kernel_config(kernel_id: str):
    """Get current configuration for a kernel"""
    config = {
        "kernel_id": kernel_id,
        "config": {
            "max_memory_gb": 8,
            "max_tables": 100,
            "auto_optimize": True,
            "log_level": "INFO"
        }
    }
    return config


@router.put("/{kernel_id}/config")
async def update_kernel_config(kernel_id: str, config_data: KernelConfig):
    """Update configuration for a kernel"""
    return {
        "kernel_id": kernel_id,
        "status": "updated",
        "config": config_data.config
    }


# ========== WEBSOCKET LOG STREAMING ==========

active_log_connections: Dict[str, set] = {}


@router.websocket("/ws/{kernel_id}/logs")
async def websocket_kernel_logs(websocket: WebSocket, kernel_id: str):
    """
    WebSocket endpoint for streaming kernel logs in real-time
    """
    await websocket.accept()
    
    if kernel_id not in active_log_connections:
        active_log_connections[kernel_id] = set()
    active_log_connections[kernel_id].add(websocket)
    
    try:
        # Send initial logs
        initial_logs = [
            {"timestamp": "10:30:15", "level": "INFO", "message": "Kernel initialized", "kernel_id": kernel_id},
            {"timestamp": "10:30:16", "level": "INFO", "message": "Processing started", "kernel_id": kernel_id},
        ]
        
        for log in initial_logs:
            await websocket.send_json(log)
        
        # Simulate live logs every 2 seconds
        while True:
            await asyncio.sleep(2)
            log_entry = {
                "timestamp": "10:30:17",
                "level": "INFO",
                "message": f"Processing task for {kernel_id}",
                "kernel_id": kernel_id
            }
            await websocket.send_json(log_entry)
            
    except WebSocketDisconnect:
        active_log_connections[kernel_id].discard(websocket)
    except Exception as e:
        print(f"WebSocket error for {kernel_id}: {e}")
        active_log_connections[kernel_id].discard(websocket)
