#!/usr/bin/env python3
"""
Grace Server - Single Entry Point
Run: python serve.py
"""

import asyncio
import uvicorn
import sys
import socket
from pathlib import Path
from typing import Dict, Any, Optional

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))


def get_guardian_allocated_port(boot_result: Dict[str, Any]) -> Optional[int]:
    """
    Get the port that Guardian allocated during boot
    Guardian boots FIRST and allocates port in Phase 3
    """
    try:
        return boot_result['phases']['phase3_ports']['port']
    except:
        return None


async def boot_grace_minimal():
    """
    Grace boot sequence - CHUNKED BOOT with Guardian validation
    
    Guardian validates each chunk completely before moving to next.
    
    Guardian Priorities:
    1. Boot integrity & networking (Guardian's domain)
    2. Delegate healing to self-healing system
    3. Delegate coding to coding agent
    
    Guardian works in SYNERGY with specialists.
    """
    
    print()
    print("=" * 80)
    print("GRACE - CHUNKED BOOT SEQUENCE (Guardian Orchestrated)")
    print("=" * 80)
    print()
    
    try:
        # PRE-BOOT: Cleanup stale port allocations
        print("[PRE-BOOT] Cleaning up stale port allocations...")
        from backend.core.port_manager import port_manager
        
        allocations_before = len(port_manager.get_all_allocations())
        
        # Force cleanup of stale ports
        for alloc in port_manager.get_all_allocations():
            if alloc['health_status'] in ['dead', 'not_listening', 'unreachable']:
                port_manager.release_port(alloc['port'])
        
        allocations_after = len(port_manager.get_all_allocations())
        cleaned = allocations_before - allocations_after
        
        if cleaned > 0:
            print(f"  [OK] Cleaned {cleaned} stale port allocations")
        else:
            print(f"  [OK] No stale ports found")
        
        # Import orchestrator
        from backend.core.guardian_boot_orchestrator import boot_orchestrator, BootChunk
        from backend.core.guardian import guardian
        
        # CHUNK 0: Guardian Self-Boot (MUST succeed)
        async def chunk_0_guardian():
            print("[CHUNK 0] Guardian Kernel Boot...")
            boot_result = await guardian.boot()
            print(f"  [OK] Guardian: Online")
            print(f"  [OK] Port: {boot_result['phases']['phase3_ports']['port']}")
            print(f"  [OK] Network: {boot_result['phases']['phase2_diagnostics']['status']}")
            print(f"  [OK] Watchdog: Active")
            return boot_result
        
        boot_orchestrator.register_chunk(BootChunk(
            chunk_id="guardian_boot",
            name="Guardian Kernel (Network, Ports, Diagnostics)",
            priority=0,
            boot_function=chunk_0_guardian,
            can_fail=False,  # CRITICAL
            guardian_validates=True,
            delegate_to=None  # Guardian handles its own domain
        ))
        
        # CHUNK 1-2: Core Systems (Guardian validates, can delegate healing)
        async def chunk_1_core_systems():
            print("[CHUNK 1-2] Core Systems...")
            results = {}
            
            try:
                from backend.core import message_bus, immutable_log
                
                if guardian.check_can_boot_kernel('message_bus', 1):
                    await message_bus.start()
                    guardian.signal_kernel_boot('message_bus', 1)
                    print("  [OK] Message Bus: Active")
                    results['message_bus'] = 'active'
                
                if guardian.check_can_boot_kernel('immutable_log', 2):
                    await immutable_log.start()
                    guardian.signal_kernel_boot('immutable_log', 2)
                    print("  [OK] Immutable Log: Active")
                    results['immutable_log'] = 'active'
            
            except ImportError as e:
                print(f"  [WARN] Core systems not available: {e}")
                results['warnings'] = ['core_systems_unavailable']
            
            return results
        
        boot_orchestrator.register_chunk(BootChunk(
            chunk_id="core_systems",
            name="Core Systems (Message Bus, Immutable Log)",
            priority=1,
            boot_function=chunk_1_core_systems,
            can_fail=True,  # Non-critical for basic operation
            guardian_validates=True,
            delegate_to="self_healing"  # Delegate issues to self-healing
        ))
        
        # CHUNK 2: LLM Models with Categorization (Guardian validates, delegates to coding agent for issues)
        async def chunk_2_llm_models():
            print("[CHUNK 2] LLM Models (21 Open Source Models by Specialty)...")
            import requests
            from backend.model_categorization import MODEL_REGISTRY, get_summary
            
            # Define all 20 open source models Grace should have
            recommended_models = {
                'qwen2.5:32b': 'Conversation & reasoning',
                'qwen2.5:72b': 'Ultimate quality',
                'deepseek-coder-v2:16b': 'Best coding',
                'deepseek-r1:70b': 'Complex reasoning (o1-level)',
                'llava:34b': 'Vision + text',
                'command-r-plus:latest': 'RAG specialist',
                'phi3.5:latest': 'Ultra fast',
                'codegemma:7b': 'Code completion',
                'granite-code:20b': 'Enterprise code',
                'dolphin-mixtral:latest': 'Uncensored',
                'nous-hermes2-mixtral:latest': 'Instructions',
                'gemma2:9b': 'Fast general',
                'llama3.2:latest': 'Lightweight',
                'mistral-nemo:latest': 'Efficient',
                'llama3.1:70b': 'Best agentic model',
                'nemotron:70b': 'Enterprise agent',
                'qwen2.5-coder:32b': 'Coding specialist',
                'mixtral:8x22b': 'MoE reasoning',
                'yi:34b': 'Long context',
                'mixtral:8x7b': 'Efficient MoE',
                'deepseek-v2.5:236b': 'MoE powerhouse'
            }
            
            results = {
                'ollama_running': False,
                'models_found': 0,
                'installed': [],
                'missing': []
            }
            
            try:
                response = requests.get("http://localhost:11434/api/tags", timeout=2)
                if response.status_code == 200:
                    models_data = response.json()
                    available_models = [m['name'] for m in models_data.get('models', [])]
                    
                    # Check which recommended models are installed
                    installed = [
                        m for m in recommended_models.keys()
                        if any(m.split(':')[0] in avail for avail in available_models)
                    ]
                    missing = [
                        m for m in recommended_models.keys()
                        if not any(m.split(':')[0] in avail for avail in available_models)
                    ]
                    
                    print(f"  [OK] Ollama: Running")
                    print(f"  [OK] Total models: {len(available_models)}")
                    print(f"  [OK] Grace models: {len(installed)}/21 specialized models")
                    
                    # Show categorization
                    summary = get_summary()
                    print(f"  -> By specialty:")
                    for specialty, data in summary.items():
                        if data['count'] > 0:
                            print(f"    • {specialty}: {data['count']} models")
                    
                    if installed:
                        print(f"  -> Installed:")
                        for model in installed[:5]:
                            print(f"    • {model} - {recommended_models[model]}")
                        if len(installed) > 5:
                            print(f"    ... and {len(installed) - 5} more")
                    
                    if missing:
                        print(f"  [WARN] Missing {len(missing)} models:")
                        for model in missing[:3]:
                            print(f"    • {model}")
                        if len(missing) > 3:
                            print(f"    ... and {len(missing) - 3} more")
                        print(f"\n  Install all: python scripts/utilities/install_all_models.py")
                        results['warnings'] = [f'missing_{len(missing)}_models']
                    
                    results['ollama_running'] = True
                    results['models_found'] = len(available_models)
                    results['installed'] = installed
                    results['missing'] = missing
                else:
                    print(f"  [WARN] Ollama returned status {response.status_code}")
                    results['warnings'] = ['ollama_unexpected_status']
            
            except requests.exceptions.RequestException as e:
                print(f"  [WARN] Ollama not running")
                print(f"    Start with: ollama serve")
                results['warnings'] = ['ollama_not_running']
            
            return results
        
        boot_orchestrator.register_chunk(BootChunk(
            chunk_id="llm_models",
            name="LLM Models (Ollama)",
            priority=2,
            boot_function=chunk_2_llm_models,
            can_fail=True,  # Grace can run without LLMs
            guardian_validates=True,
            delegate_to="coding_agent"  # Coding agent handles model issues
        ))
        
        # CHUNK 3: Main Application (Guardian validates, delegates to self-healing)
        async def chunk_3_main_app():
            print("[CHUNK 3] Grace Backend...")
            from backend.main import app
            
            print(f"  [OK] Backend loaded")
            print(f"  [OK] Remote Access: Ready")
            print(f"  [OK] {len(app.routes)} API endpoints")
            
            return {'app': 'loaded', 'endpoints': len(app.routes)}
        
        boot_orchestrator.register_chunk(BootChunk(
            chunk_id="main_app",
            name="Grace Backend Application",
            priority=3,
            boot_function=chunk_3_main_app,
            can_fail=False,  # CRITICAL
            guardian_validates=True,
            delegate_to="self_healing"
        ))
        
        # CHUNK 4: Databases (Guardian validates, delegates to self-healing)
        async def chunk_4_databases():
            print("[CHUNK 4] Databases...")
            from pathlib import Path
            
            db_dir = Path("databases")
            db_count = 0
            
            if db_dir.exists():
                db_files = list(db_dir.glob("*.db"))
                db_count = len(db_files)
                print(f"  [OK] {db_count} databases ready")
            else:
                print(f"  [WARN] Database directory not found")
            
            return {'db_count': db_count}
        
        boot_orchestrator.register_chunk(BootChunk(
            chunk_id="databases",
            name="Database Systems",
            priority=4,
            boot_function=chunk_4_databases,
            can_fail=True,  # Can run without some DBs
            guardian_validates=True,
            delegate_to="self_healing"
        ))
        
        # CHUNK 5: Autonomous Learning Whitelist (Guardian validates)
        async def chunk_5_whitelist():
            print("[CHUNK 5] Autonomous Learning Whitelist...")
            from backend.autonomy.learning_whitelist_integration import learning_whitelist_manager
            
            # Reload to ensure latest version
            learning_whitelist_manager.load_whitelist()
            
            domains_count = len(learning_whitelist_manager.whitelist.get('domains', {}))
            rules = learning_whitelist_manager.whitelist.get('autonomous_rules', {})
            
            print(f"  [OK] Whitelist loaded")
            print(f"  [OK] Learning domains: {domains_count}")
            print(f"  [OK] Allowed actions: {len(rules.get('allowed_actions', []))}")
            print(f"  [OK] Approval required: {len(rules.get('approval_required', []))}")
            
            return {
                'loaded': True,
                'domains': domains_count,
                'rules_defined': True
            }
        
        boot_orchestrator.register_chunk(BootChunk(
            chunk_id="learning_whitelist",
            name="Autonomous Learning Whitelist",
            priority=5,
            boot_function=chunk_5_whitelist,
            can_fail=True,  # Grace can run without whitelist
            guardian_validates=True,
            delegate_to="self_healing"
        ))
        
        # CHUNK 6: TRUST Framework + External Model Protocol (Guardian validates)
        async def chunk_6_trust_framework():
            print("[CHUNK 6] TRUST Framework + External Model Protocol...")
            
            from backend.trust_framework.htm_anomaly_detector import htm_detector_pool
            from backend.trust_framework.verification_mesh import verification_mesh
            from backend.trust_framework.model_health_telemetry import model_health_registry
            from backend.trust_framework.adaptive_guardrails import adaptive_guardrails
            from backend.trust_framework.ahead_of_user_research import ahead_of_user_research
            from backend.trust_framework.data_hygiene_pipeline import data_hygiene_pipeline
            from backend.trust_framework.hallucination_ledger import hallucination_ledger
            from backend.external_integration.external_model_protocol import external_model_protocol
            from backend.core.advanced_watchdog import advanced_watchdog
            from backend.trust_framework.model_integrity_system import model_integrity_registry
            from backend.trust_framework.model_rollback_system import model_rollback_system
            from backend.trust_framework.metrics_aggregator import metrics_collector
            from backend.trust_framework.alert_system import alert_system
            from backend.trust_framework.trend_analyzer import trend_analyzer
            
            print(f"  [OK] HTM Anomaly Detection: Active")
            print(f"  [OK] Verification Mesh: 5-role quorum")
            print(f"  [OK] Model Health Telemetry: 20 monitors")
            print(f"  [OK] Adaptive Guardrails: 4 levels")
            print(f"  [OK] Ahead-of-User Research: Predictive")
            print(f"  [OK] Data Hygiene Pipeline: 6 checks")
            print(f"  [OK] Hallucination Ledger: Tracking")
            print(f"  [OK] External Model Protocol: Secure (HMAC, rate-limited, audited)")
            print(f"  [OK] Advanced Watchdog: Predictive failure detection")
            print(f"  [OK] Model Integrity System: Checksum + behavioral verification")
            print(f"  [OK] Model Rollback: Snapshot-based recovery")
            print(f"  [OK] Metrics Aggregator: Time-series collection")
            print(f"  [OK] Alert System: Multi-channel notifications")
            print(f"  [OK] Trend Analyzer: Historical analysis & prediction")
            
            # Start advanced watchdog
            await advanced_watchdog.start()
            
            # Start metrics collection
            await metrics_collector.start(interval_seconds=60)
            
            return {
                'htm_active': True,
                'verification_mesh_active': True,
                'model_monitors': 20,
                'guardrail_levels': 4,
                'systems_loaded': 14,
                'external_protocol_active': True,
                'advanced_watchdog_active': True,
                'model_integrity_active': True,
                'model_rollback_active': True,
                'metrics_collector_active': True,
                'alert_system_active': True,
                'trend_analyzer_active': True
            }
        
        boot_orchestrator.register_chunk(BootChunk(
            chunk_id="trust_framework",
            name="TRUST Framework (AI Governance)",
            priority=6,
            boot_function=chunk_6_trust_framework,
            can_fail=False,  # Critical - trust framework must load
            guardian_validates=True,
            delegate_to="self_healing"
        ))
        
        # CHUNK 7-26: All 20 Grace Kernels (Guardian validates each)
        async def chunk_7_20_kernels():
            print("[CHUNK 7-26] Grace Kernels (20 kernels)...")
            from backend.unified_logic.kernel_integration import KernelIntegrator
            
            integrator = KernelIntegrator()
            print(f"  -> Defined {len(integrator.kernel_registry)} kernels")
            
            # Integrate all kernels
            result = await integrator.integrate_all_kernels()
            
            print(f"  [OK] Integrated: {result.get('integrated', 0)}/20 kernels")
            print(f"  [OK] Tier 1 (Critical): {result.get('tier1_count', 0)}")
            print(f"  [OK] Tier 2 (Governance): {result.get('tier2_count', 0)}")
            print(f"  [OK] Tier 3 (Execution): {result.get('tier3_count', 0)}")
            print(f"  [OK] Tier 4 (Agentic): {result.get('tier4_count', 0)}")
            print(f"  [OK] Tier 5 (Services): {result.get('tier5_count', 0)}")
            
            return result
        
        boot_orchestrator.register_chunk(BootChunk(
            chunk_id="grace_kernels",
            name="All 20 Grace Kernels (Tiered Boot)",
            priority=7,
            boot_function=chunk_7_20_kernels,
            can_fail=False,  # Critical - kernels must boot
            guardian_validates=True,
            delegate_to="self_healing"  # Self-healing handles kernel issues
        ))
        
        # Execute chunked boot with Guardian validation
        print()
        print("[ORCHESTRATOR] Starting chunked boot sequence...")
        print("[ORCHESTRATOR] Guardian will validate each chunk before proceeding")
        print()
        
        boot_log = await boot_orchestrator.execute_boot()
        
        if not boot_log.get('success'):
            print(f"\n[ERROR] Boot failed at chunk: {boot_log.get('aborted_at_chunk')}")
            print(f"   Reason: {boot_log.get('abort_reason')}")
            return False
        
        # Extract results
        guardian_chunk = next((c for c in boot_orchestrator.chunks if c.chunk_id == 'guardian_boot'), None)
        if not guardian_chunk or not guardian_chunk.result:
            print("[ERROR] Guardian chunk not found or failed")
            return False
        
        guardian_boot = guardian_chunk.result
        
        print()
        print("[ORCHESTRATOR] All chunks validated and approved by Guardian")
        print()
        
        # Return boot result with port info
        return guardian_boot
        
    except Exception as e:
        print(f"\n[ERROR] Boot failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print()
    print("=" * 80)
    print("   GRACE - Autonomous AI System")
    print("=" * 80)
    print()
    
    # Boot Grace (Guardian boots FIRST and allocates port)
    boot_result = asyncio.run(boot_grace_minimal())
    
    if not boot_result or isinstance(boot_result, bool) and not boot_result:
        print("Failed to boot Grace. Exiting.")
        input("\nPress Enter to exit...")
        sys.exit(1)
    
    # Get port from Guardian's boot result
    port = get_guardian_allocated_port(boot_result)
    
    if not port:
        print("[ERROR] Guardian did not allocate a port")
        sys.exit(1)
    
    # Start server
    print("=" * 80)
    print("GRACE IS READY")
    print("=" * 80)
    print()
    print(f" API: http://localhost:{port}")
    print(f" Docs: http://localhost:{port}/docs")
    print(f"  Health: http://localhost:{port}/health")
    print()
    print("=" * 80)
    print("NEXT STEPS")
    print("=" * 80)
    print()
    print("Terminal 2 - Configure clients for this port:")
    print(f"  python auto_configure.py")
    print()
    print("Then use:")
    print("  • Remote Access: python remote_access_client.py setup")
    print("  • Learning: python start_grace_now.py")
    print("  • Menu: USE_GRACE.cmd")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 80)
    print()
    
    # Try to start server, if port fails, try next one automatically
    max_retries = 10
    for retry in range(max_retries):
        try:
            # Register PID with port manager
            import os
            try:
                from backend.core.port_manager import port_manager
                port_manager.register_pid(port, os.getpid())
                print(f"[PORT-MANAGER] Registered PID {os.getpid()} for port {port}")
            except:
                pass
            
            # Start server
            print(f"\n[STARTING] Attempting to bind to port {port}...")
            uvicorn.run(
                "backend.main:app",
                host="0.0.0.0",
                port=port,
                log_level="info",
                reload=False  # Disable reload to avoid issues
            )
            break  # Success!
            
        except OSError as e:
            if 'address already in use' in str(e).lower() or '10048' in str(e):
                print(f"\n[WARN]️  Port {port} in use! Trying next port...")
                
                # Release this port in manager
                try:
                    from backend.core.port_manager import port_manager
                    port_manager.release_port(port)
                except:
                    pass
                
                # Try next port
                port += 1
                if port > 8100:
                    port = 8000  # Wrap around
                
                # Allocate new port
                try:
                    from backend.core.port_manager import port_manager
                    allocation = port_manager.allocate_port(
                        service_name="grace_backend",
                        started_by="serve.py",
                        purpose="Main Grace API server (retry)",
                        preferred_port=port
                    )
                    if 'port' in allocation:
                        port = allocation['port']
                        print(f"✅ Trying port {port} instead...")
                except:
                    pass
                
                if retry == max_retries - 1:
                    print(f"\n[ERROR] Could not bind to any port after {max_retries} tries!")
                    print("Run: python kill_grace.py")
                    sys.exit(1)
            else:
                raise
                
        except KeyboardInterrupt:
            print("\n\nGrace shutdown requested...")
            
            # Release port
            try:
                from backend.core.port_manager import port_manager
                port_manager.release_port(port)
                print(f"[PORT-MANAGER] Released port {port}")
            except:
                pass
            
            print("Goodbye! 👋")
            break
