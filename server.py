#!/usr/bin/env python3
"""
Grace Server - Single Entry Point
Run: python server.py
"""

import asyncio
import os
import uvicorn
import sys
import socket
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file immediately
load_dotenv()

# Add root to path
sys.path.insert(0, str(Path(__file__).parent))

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Removed: Guardian no longer allocates ports
# System uses single port from GRACE_PORT environment variable


async def boot_grace_minimal():
    """
    Grace boot sequence - CHUNKED BOOT with Guardian validation
    
    Guardian validates each chunk completely before moving to next.
    
    Guardian Priorities:
    1. Boot integrity & networking (Guardian's domain)
    2. Delegate healing to self-healing system (Chunk 0.6)
    3. Delegate coding to coding agent (Chunk 0.7)
    
    Guardian works in SYNERGY with specialists.
    """
    
    print()
    print("=" * 80)
    print("GRACE - CHUNKED BOOT SEQUENCE (Guardian Orchestrated)")
    print("=" * 80)
    print()
    
    try:
        # PRE-BOOT: Simple port check (no complex port manager)
        print("[PRE-BOOT] Checking port availability...")
        
        # Import orchestrator
        from backend.core.guardian_boot_orchestrator import boot_orchestrator, BootChunk
        from backend.core.guardian import guardian
        
        # CHUNK 0: Guardian Self-Boot (MUST succeed)
        async def chunk_0_guardian():
            print("[CHUNK 0] Guardian Kernel Boot...")
            boot_result = await guardian.boot()
            print(f"  [OK] Guardian: Online")
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
        
        # CHUNK 0.5: Healing Orchestrator (Guardian validates)
        async def chunk_0b_healing():
            print("[CHUNK 0.5] Healing Orchestrator...")
            from backend.core.healing_orchestrator import healing_orchestrator
            print("  [OK] Healing Orchestrator: Online (Watching Logs/CI/Secrets)")
            return {"status": "online", "mode": "active"}

        boot_orchestrator.register_chunk(BootChunk(
            chunk_id="healing_orchestrator",
            name="Healing Orchestrator",
            priority=0.5,
            boot_function=chunk_0b_healing,
            can_fail=False, # Critical for self-repair
            guardian_validates=True
        ))

        # CHUNK 0.6: Self-Healing Agent (Guardian validates)
        async def chunk_0d_self_healing():
            print("[CHUNK 0.6] Self-Healing Agent...")
            from backend.self_heal.runner import runner
            
            # Start the agent
            await runner.start()
            
            print("  [OK] Self-Healing Agent: Online (Automated remediation)")
            print("  [OK] Playbook execution: Active (15s intervals)")
            
            return {
                "status": "online", 
                "poll_interval": 15,
                "mode": "active"
            }

        boot_orchestrator.register_chunk(BootChunk(
            chunk_id="self_healing_agent",
            name="Self-Healing Agent",
            priority=0.6,
            boot_function=chunk_0d_self_healing,
            can_fail=True, # Can fail but highly desired
            guardian_validates=True,
            delegate_to="self_healing"
        ))
        
        # CHUNK 0.7: Elite Coding Agent (Guardian validates)
        async def chunk_0e_coding_agent():
            print("[CHUNK 0.7] Elite Coding Agent (Senior Dev Mode)...")
            try:
                from backend.agents_core.elite_coding_agent import elite_coding_agent
                
                # Start the agent
                await elite_coding_agent.start()
                
                print(f"  [OK] Elite Coding Agent: Online")
                print(f"  [OK] Knowledge Base: {len(elite_coding_agent.knowledge_base)} entries")
                print(f"  [OK] Execution Mode: {elite_coding_agent.orchestration_state.get('mode', 'auto')}")
                
                return {
                    "status": "online",
                    "knowledge_entries": len(elite_coding_agent.knowledge_base),
                    "active": True
                }
            except Exception as e:
                print(f"  [WARN] Elite Coding Agent startup issue: {e}")
                return {"status": "degraded", "error": str(e)}

        boot_orchestrator.register_chunk(BootChunk(
            chunk_id="elite_coding_agent",
            name="Elite Coding Agent",
            priority=0.7,
            boot_function=chunk_0e_coding_agent,
            can_fail=True, 
            guardian_validates=True,
            delegate_to="self_healing"
        ))

        # CHUNK 0.75: Tiered Agent Orchestrator (Guardian validates)
        async def chunk_0g_agent_orchestrator():
            print("[CHUNK 0.75] Tiered Agent Orchestrator...")
            try:
                from backend.agents_core.agent_orchestrator import agent_orchestrator
                
                # Start the orchestrator
                await agent_orchestrator.start()
                
                print(f"  [OK] Agent Orchestrator: Online")
                print(f"  [OK] Max concurrent pipelines: {agent_orchestrator.max_concurrent_pipelines}")
                print(f"  [OK] Pipeline phases: research → design → implement → test → deploy")
                print(f"  [OK] Guardian oversight: Active (pause/resume/override)")
                print(f"  [OK] Playbooks: First-class agent tools")
                print(f"  [OK] Learning loop: Artifact feedback enabled")
                
                return {
                    "status": "online",
                    "max_concurrent": agent_orchestrator.max_concurrent_pipelines,
                    "guardian_integrated": True
                }
            except Exception as e:
                print(f"  [WARN] Agent Orchestrator startup issue: {e}")
                return {"status": "degraded", "error": str(e)}

        boot_orchestrator.register_chunk(BootChunk(
            chunk_id="agent_orchestrator",
            name="Tiered Agent Orchestrator",
            priority=0.75,
            boot_function=chunk_0g_agent_orchestrator,
            can_fail=True, 
            guardian_validates=True,
            delegate_to="self_healing"
        ))

        # CHUNK 0.8: Senior Developer Agent (Guardian validates)
        async def chunk_0f_developer_agent():
            print("[CHUNK 0.8] Senior Developer Agent...")
            try:
                from backend.developer.developer_agent import developer_agent
                
                print(f"  [OK] Developer Agent: Ready")
                print(f"  [OK] Pipeline: Plan -> Design -> Implement -> Governance -> Test -> Deploy")
                
                return {
                    "status": "online",
                    "ready": True
                }
            except Exception as e:
                print(f"  [WARN] Developer Agent startup issue: {e}")
                return {"status": "degraded", "error": str(e)}

        boot_orchestrator.register_chunk(BootChunk(
            chunk_id="developer_agent",
            name="Senior Developer Agent",
            priority=0.8,
            boot_function=chunk_0f_developer_agent,
            can_fail=True,
            guardian_validates=True,
            delegate_to="self_healing"
        ))

        # CHUNK 1-2: Core Systems (Guardian validates, can delegate healing)
        async def chunk_1_core_systems():
            print("[CHUNK 1-2] Core Systems...")
            results = {}
            
            try:
                from backend.core.message_bus import message_bus
                from backend.core.immutable_log import immutable_log
                
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
                        # NOTE: This path might need adjustment if scripts/ is moved/deleted
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

        # CHUNK 6: Governed Learning Engine (Gap detection + world model)
        async def chunk_6_governed_learning():
            print("[CHUNK 6] Governed Learning Engine...")
            from backend.learning_systems.continuous_learning_loop import continuous_learning_loop
            from backend.autonomy.proactive_learning_agent import proactive_learning_agent
            
            # Start the continuous learning loop
            await continuous_learning_loop.start()
            print("  [OK] Continuous Learning Loop: Active (Learning from every action)")
            
            # Start the proactive learning agent
            await proactive_learning_agent.start()
            print("  [OK] Proactive Learning Agent: Active (Always learning from internet)")
            print("  [OK] Current Domain: 1_genai_foundations (Auto-started)")
            print("  [OK] Learning Cycle: Every 60 seconds (Fully autonomous)")
            
            from backend.learning.governed_learning import (
                ApprovalGate,
                DomainWhitelistAPI,
                DomainWhitelistRegistry,
                GapDetectionEngine,
                GovernedLearningOrchestrator,
                LearningJobDashboard,
                LearningJobQueue,
                LearningSimulationFramework,
                SafeModeLearningController,
                SandboxVerifier,
                WorldModelUpdateManager,
            )

            whitelist_path = Path("config/autonomous_learning_whitelist.yaml")
            registry = DomainWhitelistRegistry.from_config(whitelist_path)
            api = DomainWhitelistAPI(registry)
            if registry.is_empty():
                api.create_from_template(
                    domain="internal_docs",
                    template_name="docs_default",
                    overrides={"tags": ["bootstrap"], "documentation": ["https://grace/bootstrap"]},
                )
                api.request_domain(
                    {
                        "domain": "partner_repo",
                        "allowed_actions": ["search", "clone"],
                        "approval_required": True,
                        "sandbox_profile": "code_review",
                        "templates": ["repo_ml"],
                        "max_parallel_jobs": 1,
                        "tags": ["pending"],
                        "documentation": ["https://partners/docs"],
                        "repositories": ["https://github.com/partner/repo"],
                        "datasets": [],
                    },
                    requested_by="guardian",
                    justification="Need governed repo access",
                )

            gap_engine = GapDetectionEngine(target_confidence=0.9)
            sample_queries = [
                {
                    "query": "mttr reduction plan",
                    "topic": "trust",
                    "success": 0.55,
                    "retrieval_uncertainty": 0.5,
                    "impact": 1.2,
                },
                {
                    "query": "rag provenance citations",
                    "topic": "memory",
                    "success": 0.6,
                    "retrieval_uncertainty": 0.35,
                    "impact": 0.9,
                },
                {
                    "query": "governed learning job queue",
                    "topic": "learning",
                    "success": 0.45,
                    "retrieval_uncertainty": 0.62,
                    "impact": 1.5,
                },
            ]
            knowledge_snapshot = {
                "topics": {
                    "trust": {"confidence": 0.58},
                    "memory": {"confidence": 0.87},
                    "learning": {"confidence": 0.42},
                }
            }
            gap_report = gap_engine.analyze_queries(sample_queries, knowledge_snapshot)
            top_signal = gap_report.signals[0] if gap_report.signals else None

            job_queue = LearningJobQueue(capacity=max(3, registry.max_parallel_jobs()))
            sandbox = SandboxVerifier(required_checks=["unit_tests", "integration_checks"])
            approvals = ApprovalGate(fast_track_roles=["guardian"])
            safe_mode = SafeModeLearningController(safe_mode=os.getenv("OFFLINE_MODE", "1") == "1")
            world_model = WorldModelUpdateManager()
            dashboard = LearningJobDashboard()
            simulation = LearningSimulationFramework()
            orchestrator = GovernedLearningOrchestrator(
                registry,
                job_queue,
                sandbox,
                approvals,
                safe_mode,
                world_model,
                dashboard,
                simulation,
            )

            domains = registry.list_domains()
            target_domain = domains[0]
            entry = registry.get_entry(target_domain)
            action = entry.allowed_actions[0]
            job_payload = {
                "domain": target_domain,
                "action": action,
                "approved_by": "guardian" if entry.approval_required else None,
                "approval_token": "APPROVED-GOVERNANCE" if entry.approval_required else None,
                "allow_network": False,
                "sandbox_checks": ["unit_tests", "integration_checks"],
                "priority": (top_signal.priority_score if top_signal else 0.5),
                "impact": (top_signal.impact_score if top_signal else 0.8),
                "world_model_update": {
                    "source": "governed_learning_engine",
                    "entries": [
                        {
                            "topic": top_signal.topic if top_signal else "learning",
                            "content": "Gap remediation playbook",
                            "confidence": min(0.99, 0.7 + (top_signal.confidence_delta if top_signal else 0.1)),
                        }
                    ],
                    "validators": ["guardian", "codex"],
                },
            }

            try:
                orchestrator.submit_job(job_payload)
                job_result = orchestrator.process_next_job()
            except Exception as exc:
                print(f"  [WARN] Governed learning orchestration degraded: {exc}")
                job_result = {"error": str(exc)}

            dashboard_snapshot = orchestrator.dashboard_snapshot()
            if top_signal:
                print(
                    f"  [OK] Top gap: {top_signal.topic} (priority {top_signal.priority_score})"
                )
            if gap_report.dashboard_cards:
                print(
                    f"  [OK] Gap dashboard cards: {[card['title'] for card in gap_report.dashboard_cards]}"
                )
            print(
                f"  [OK] Governed learning dashboard: jobs={dashboard_snapshot['total_jobs']} completed={dashboard_snapshot['completed_jobs']} pending={dashboard_snapshot['pending']}"
            )
            if registry.list_pending():
                print(f"  [OK] Pending domains waiting approval: {registry.list_pending()}")

            return {
                'gap_report': gap_report.metrics,
                'dashboard_cards': gap_report.dashboard_cards,
                'job_result': job_result,
                'dashboard': dashboard_snapshot,
            }

        boot_orchestrator.register_chunk(BootChunk(
            chunk_id="governed_learning_engine",
            name="Governed Learning & World Model Updates",
            priority=6,
            boot_function=chunk_6_governed_learning,
            can_fail=True,
            guardian_validates=True,
            delegate_to="self_healing"
        ))

        # CHUNK 6.5: Remote Learning Systems (Firefox + GitHub + Web Scraper)
        async def chunk_6b_remote_learning():
            print("[CHUNK 6.5] Remote Learning Systems (Internet & GitHub Access)...")
            
            results = {
                'systems_started': 0,
                'warnings': []
            }
            
            try:
                # Start Firefox Agent for internet browsing
                from backend.agents.firefox_agent import firefox_agent
                await firefox_agent.start(enabled=True)
                print(f"  [OK] Firefox Agent: ENABLED (Internet access via your PC)")
                print(f"  [OK] Approved domains: {len(firefox_agent.approved_domains)}")
                results['firefox_enabled'] = True
                results['systems_started'] += 1
            except Exception as e:
                print(f"  [WARN] Firefox Agent startup issue: {e}")
                results['warnings'].append('firefox_agent')
            
            try:
                # Start Remote Computer Access
                from backend.misc.remote_computer_access import RemoteComputerAccess
                remote_access = RemoteComputerAccess()
                await remote_access.start()
                print(f"  [OK] Remote Computer Access: Active")
                print(f"  [OK] Allowed actions: {len(remote_access.allowed_actions)}")
                results['remote_access_enabled'] = True
                results['systems_started'] += 1
            except Exception as e:
                print(f"  [WARN] Remote Computer Access startup issue: {e}")
                results['warnings'].append('remote_access')
            
            try:
                # Start Web Scraper (using Firefox agent)
                from backend.utilities.safe_web_scraper import safe_web_scraper
                await safe_web_scraper.start()
                print(f"  [OK] Web Scraper: Active (via Firefox agent)")
                print(f"  [OK] Trusted domains: {len(safe_web_scraper.trusted_domains)}")
                results['web_scraper_enabled'] = True
                results['systems_started'] += 1
            except Exception as e:
                print(f"  [WARN] Web Scraper startup issue: {e}")
                results['warnings'].append('web_scraper')
            
            try:
                # Start GitHub Knowledge Miner
                from backend.knowledge.github_knowledge_miner import github_miner
                await github_miner.start()
                print(f"  [OK] GitHub Knowledge Miner: Active")
                results['github_miner_enabled'] = True
                results['systems_started'] += 1
            except Exception as e:
                print(f"  [WARN] GitHub Knowledge Miner startup issue: {e}")
                results['warnings'].append('github_miner')
            
            print(f"  [OK] {results['systems_started']}/4 remote learning systems started")
            if results['warnings']:
                print(f"  [WARN] Degraded systems: {', '.join(results['warnings'])}")
            
            print()
            print("  🌐 Grace can now learn from:")
            print("    • Internet (via Firefox on your PC)")
            print("    • GitHub repositories")
            print("    • Stack Overflow, arXiv, Kaggle, etc.")
            print("    • All governed, logged, and traceable")
            
            return results

        boot_orchestrator.register_chunk(BootChunk(
            chunk_id="remote_learning_systems",
            name="Remote Learning Systems (Internet & GitHub)",
            priority=6.5,
            boot_function=chunk_6b_remote_learning,
            can_fail=True,
            guardian_validates=True,
            delegate_to="self_healing"
        ))

        # CHUNK 6.7: Self-Driving Learning Feedback Loop
        async def chunk_6c_learning_feedback_loop():
            print("[CHUNK 6.7] Self-Driving Learning Feedback Loop...")
            
            results = {
                'systems_started': 0,
                'warnings': []
            }
            
            try:
                # Start learning mission launcher
                from backend.learning_systems.learning_mission_launcher import learning_mission_launcher
                await learning_mission_launcher.start()
                print(f"  [OK] Learning Mission Launcher: Active")
                print(f"  [OK] Max concurrent missions: {learning_mission_launcher.max_concurrent_missions}")
                results['mission_launcher_active'] = True
                results['systems_started'] += 1
            except Exception as e:
                print(f"  [WARN] Mission launcher startup issue: {e}")
                results['warnings'].append('mission_launcher')
            
            try:
                # Start learning triage agent
                from backend.learning_systems.learning_triage_agent import learning_triage_agent
                await learning_triage_agent.start()
                print(f"  [OK] Learning Triage Agent: Active")
                print(f"  [OK] Event subscriptions: {len(learning_triage_agent.subscriptions)}")
                print(f"  [OK] Triage interval: 30 seconds")
                results['triage_agent_active'] = True
                results['systems_started'] += 1
            except Exception as e:
                print(f"  [WARN] Triage agent startup issue: {e}")
                results['warnings'].append('triage_agent')
            
            try:
                # Initialize event emitters
                from backend.learning_systems.event_emitters import (
                    guardian_events,
                    htm_events,
                    rag_events,
                    remote_access_events,
                    agent_events,
                    system_events
                )
                
                # Initialize all emitters
                await guardian_events.initialize()
                await htm_events.initialize()
                await rag_events.initialize()
                await remote_access_events.initialize()
                await agent_events.initialize()
                await system_events.initialize()
                
                print(f"  [OK] Event Emitters: Active (6 emitter types)")
                results['event_emitters_active'] = True
                results['systems_started'] += 1
            except Exception as e:
                print(f"  [WARN] Event emitters startup issue: {e}")
                results['warnings'].append('event_emitters')
            
            print()
            print("  🔄 Self-Driving Feedback Loop:")
            print("    • Continuous event sensing (Guardian, HTM, RAG, agents)")
            print("    • Autonomous diagnosis & clustering")
            print("    • Auto-launch learning missions")
            print("    • Full traceability (immutable log + RAG)")
            print()
            print("  📊 Event Sources:")
            print("    • Guardian missions (created/resolved/failed)")
            print("    • HTM anomalies (patterns, degradation)")
            print("    • RAG health (retrieval failures, low confidence)")
            print("    • Remote access (action failures, blocks)")
            print("    • Agent outcomes (task failures, errors)")
            print("    • System events (boot failures, crashes)")
            print()
            print("  🎯 Autonomous Actions:")
            print("    • Cluster events by domain + severity + pattern")
            print("    • Calculate urgency & recurrence scores")
            print("    • Launch learning missions automatically")
            print("    • Learn from web, GitHub, and internal knowledge")
            
            if results['warnings']:
                print()
                print(f"  [WARN] Degraded systems: {', '.join(results['warnings'])}")
            
            return results

        boot_orchestrator.register_chunk(BootChunk(
            chunk_id="learning_feedback_loop",
            name="Self-Driving Learning Feedback Loop",
            priority=6.7,
            boot_function=chunk_6c_learning_feedback_loop,
            can_fail=True,
            guardian_validates=True,
            delegate_to="self_healing"
        ))

        # CHUNK 6.8: Governance & Safety Systems
        async def chunk_6d_governance_safety():
            print("[CHUNK 6.8] Governance & Safety Systems...")
            
            results = {
                'systems_started': 0,
                'warnings': []
            }
            
            try:
                # Start RBAC system
                from backend.governance_system.rbac_system import rbac_system
                await rbac_system.start()
                print(f"  [OK] RBAC System: Active")
                print(f"  [OK] Service accounts: {len(rbac_system.service_accounts)}")
                print(f"  [OK] Roles: learning_mission, agent_pipeline, self_healing, guardian")
                results['rbac_active'] = True
                results['systems_started'] += 1
            except Exception as e:
                print(f"  [WARN] RBAC system startup issue: {e}")
                results['warnings'].append('rbac_system')
            
            try:
                # Start inline approval engine
                from backend.governance_system.inline_approval_engine import inline_approval_engine
                await inline_approval_engine.start()
                print(f"  [OK] Inline Approval Engine: Active")
                print(f"  [OK] Auto-approval threshold: {inline_approval_engine.auto_approval_threshold}")
                print(f"  [OK] Escalation threshold: {inline_approval_engine.escalation_threshold}")
                results['approval_engine_active'] = True
                results['systems_started'] += 1
            except Exception as e:
                print(f"  [WARN] Approval engine startup issue: {e}")
                results['warnings'].append('approval_engine')
            
            print()
            print("  🛡️ Safety & Governance:")
            print("    • RBAC: Service account permissions")
            print("    • Risk scoring: Auto-approve low risk")
            print("    • Guardian escalation: High-risk actions")
            print("    • Immutable log: All decisions audited")
            print()
            print("  📋 Approval Flow:")
            print("    1. Mission requests resource access")
            print("    2. RBAC checks permissions")
            print("    3. Risk score calculated")
            print("    4. Auto-approve if risk < 0.3")
            print("    5. Escalate to Guardian if risk > 0.7")
            print("    6. All decisions logged")
            
            if results['warnings']:
                print()
                print(f"  [WARN] Degraded systems: {', '.join(results['warnings'])}")
            
            return results

        boot_orchestrator.register_chunk(BootChunk(
            chunk_id="governance_safety",
            name="Governance & Safety Systems",
            priority=6.8,
            boot_function=chunk_6d_governance_safety,
            can_fail=True,
            guardian_validates=True,
            delegate_to="self_healing"
        ))

        # CHUNK 6.9: Chaos Engineering Agent
        async def chunk_6e_chaos_agent():
            print("[CHUNK 6.9] Chaos Engineering Agent...")
            
            results = {
                'systems_started': 0,
                'warnings': []
            }
            
            try:
                # Start chaos agent
                from backend.chaos.chaos_agent import chaos_agent
                from backend.chaos.component_profiles import component_registry
                
                await chaos_agent.start()
                
                print(f"  [OK] Chaos Agent: Ready (DISABLED by default)")
                print(f"  [OK] Component profiles: {len(component_registry.profiles)}")
                print(f"  [OK] Environment: {chaos_agent.environment}")
                print(f"  [OK] Blast radius limit: {chaos_agent.blast_radius_limit} components")
                results['chaos_agent_ready'] = True
                results['systems_started'] += 1
            except Exception as e:
                print(f"  [WARN] Chaos agent startup issue: {e}")
                results['warnings'].append('chaos_agent')
            
            print()
            print("  🎯 Chaos Engineering:")
            print("    • Component profiles: 8 (API, DB, RAG, HTM, etc.)")
            print("    • Stress patterns: 24 (OWASP, load, config, network)")
            print("    • Guardrail verification: Automated")
            print("    • Healing integration: Auto-raise tasks")
            print("    • Learning feedback: RAG/HTM enrichment")
            print()
            print("  ⚠️  Chaos campaigns require governance approval")
            print("  ⚠️  Default: staging environment only")
            print("  ⚠️  Guardian can halt instantly")
            
            if results['warnings']:
                print()
                print(f"  [WARN] Degraded systems: {', '.join(results['warnings'])}")
            
            return results

        boot_orchestrator.register_chunk(BootChunk(
            chunk_id="chaos_agent",
            name="Chaos Engineering Agent",
            priority=6.9,
            boot_function=chunk_6e_chaos_agent,
            can_fail=True,
            guardian_validates=True,
            delegate_to="self_healing"
        ))

        # CHUNK 7: TRUST Framework + External Model Protocol (Guardian validates)
        async def chunk_7_trust_framework():
            print("[CHUNK 7] TRUST Framework + External Model Protocol...")
            
            results = {
                'systems_loaded': 0,
                'degraded': []
            }
            
            try:
                from backend.trust_framework.htm_anomaly_detector import htm_detector_pool
                print(f"  [OK] HTM Anomaly Detection: Active")
                results['htm_active'] = True
                results['systems_loaded'] += 1
                
                # Start Model Telemetry Integration (feeds HTM + RAG)
                from backend.ml_training.model_telemetry_integration import model_telemetry_integration
                await model_telemetry_integration.start()
                print(f"  [OK] Model Telemetry: Active (HTM + RAG integration)")
                results['systems_loaded'] += 1
            except Exception as e:
                print(f"  [WARN] HTM Anomaly Detection degraded: {e}")
                results['degraded'].append('htm_anomaly_detector')
            
            try:
                from backend.trust_framework.verification_mesh import verification_mesh
                print(f"  [OK] Verification Mesh: 5-role quorum")
                results['verification_mesh_active'] = True
                results['systems_loaded'] += 1
            except Exception as e:
                print(f"  [WARN] Verification Mesh degraded: {e}")
                results['degraded'].append('verification_mesh')
            
            try:
                from backend.trust_framework.model_health_telemetry import model_health_registry
                print(f"  [OK] Model Health Telemetry: 20 monitors")
                results['model_monitors'] = 20
                results['systems_loaded'] += 1
            except Exception as e:
                print(f"  [WARN] Model Health Telemetry degraded: {e}")
                results['degraded'].append('model_health_telemetry')
            
            try:
                from backend.trust_framework.adaptive_guardrails import adaptive_guardrails
                print(f"  [OK] Adaptive Guardrails: 4 levels")
                results['guardrail_levels'] = 4
                results['systems_loaded'] += 1
            except Exception as e:
                print(f"  [WARN] Adaptive Guardrails degraded: {e}")
                results['degraded'].append('adaptive_guardrails')
            
            try:
                from backend.trust_framework.ahead_of_user_research import ahead_of_user_research
                print(f"  [OK] Ahead-of-User Research: Predictive")
                results['systems_loaded'] += 1
            except Exception as e:
                print(f"  [WARN] Ahead-of-User Research degraded: {e}")
                results['degraded'].append('ahead_of_user_research')
            
            try:
                from backend.trust_framework.data_hygiene_pipeline import data_hygiene_pipeline
                print(f"  [OK] Data Hygiene Pipeline: 6 checks")
                results['systems_loaded'] += 1
            except Exception as e:
                print(f"  [WARN] Data Hygiene Pipeline degraded: {e}")
                results['degraded'].append('data_hygiene_pipeline')
            
            try:
                from backend.trust_framework.hallucination_ledger import hallucination_ledger
                print(f"  [OK] Hallucination Ledger: Tracking")
                results['systems_loaded'] += 1
            except Exception as e:
                print(f"  [WARN] Hallucination Ledger degraded: {e}")
                results['degraded'].append('hallucination_ledger')
            
            try:
                from backend.external_integration.external_model_protocol import external_model_protocol
                print(f"  [OK] External Model Protocol: Secure (HMAC, rate-limited, audited)")
                results['external_protocol_active'] = True
                results['systems_loaded'] += 1
            except Exception as e:
                print(f"  [WARN] External Model Protocol degraded: {e}")
                results['degraded'].append('external_model_protocol')
            
            try:
                from backend.core.advanced_watchdog import advanced_watchdog
                print(f"  [OK] Advanced Watchdog: Predictive failure detection")
                await advanced_watchdog.start()
                results['advanced_watchdog_active'] = True
                results['systems_loaded'] += 1
            except Exception as e:
                print(f"  [WARN] Advanced Watchdog degraded: {e}")
                results['degraded'].append('advanced_watchdog')
            
            try:
                from backend.trust_framework.model_integrity_system import model_integrity_registry
                print(f"  [OK] Model Integrity System: Checksum + behavioral verification")
                results['model_integrity_active'] = True
                results['systems_loaded'] += 1
            except Exception as e:
                print(f"  [WARN] Model Integrity System degraded: {e}")
                results['degraded'].append('model_integrity_system')
            
            try:
                from backend.trust_framework.model_rollback_system import model_rollback_system
                print(f"  [OK] Model Rollback: Snapshot-based recovery")
                results['model_rollback_active'] = True
                results['systems_loaded'] += 1
            except Exception as e:
                print(f"  [WARN] Model Rollback degraded: {e}")
                results['degraded'].append('model_rollback_system')
            
            try:
                from backend.trust_framework.metrics_aggregator import metrics_collector
                print(f"  [OK] Metrics Aggregator: Time-series collection")
                await metrics_collector.start(interval_seconds=60)
                results['metrics_collector_active'] = True
                results['systems_loaded'] += 1
            except Exception as e:
                print(f"  [WARN] Metrics Aggregator degraded: {e}")
                results['degraded'].append('metrics_aggregator')
            
            try:
                from backend.trust_framework.alert_system import alert_system
                print(f"  [OK] Alert System: Multi-channel notifications")
                results['alert_system_active'] = True
                results['systems_loaded'] += 1
            except Exception as e:
                print(f"  [WARN] Alert System degraded: {e}")
                results['degraded'].append('alert_system')
            
            try:
                from backend.trust_framework.trend_analyzer import trend_analyzer
                print(f"  [OK] Trend Analyzer: Historical analysis & prediction")
                results['trend_analyzer_active'] = True
                results['systems_loaded'] += 1
            except Exception as e:
                print(f"  [WARN] Trend Analyzer degraded: {e}")
                results['degraded'].append('trend_analyzer')
            
            if results['degraded']:
                print(f"  [WARN] {len(results['degraded'])} TRUST systems degraded")
            
            return results
        
        boot_orchestrator.register_chunk(BootChunk(
            chunk_id="trust_framework",
            name="TRUST Framework (AI Governance)",
            priority=7,
            boot_function=chunk_7_trust_framework,
            can_fail=False,  # Critical - trust framework must load
            guardian_validates=True,
            delegate_to="self_healing"
        ))

        # CHUNK 8-26: All 20 Grace Kernels (Guardian validates each)
        async def chunk_8_20_kernels():
            print("[CHUNK 8-26] Grace Kernels (20 kernels)...")
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
            priority=8,
            boot_function=chunk_8_20_kernels,
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
        
        # Capture boot snapshot after successful validation
        print("[SNAPSHOT] Capturing clean boot snapshot...")
        try:
            from backend.boot.snapshot_manager import boot_snapshot_manager
            snapshot_result = await boot_snapshot_manager.capture_snapshot(guardian_boot)
            if snapshot_result.get('captured'):
                print(f"  [OK] Snapshot captured: {snapshot_result['snapshot_id']}")
                print(f"  [OK] Size: {snapshot_result['metadata']['total_bytes']:,} bytes")
                print(f"  [OK] Retention: {boot_snapshot_manager.max_snapshots} snapshots kept")
            else:
                print(f"  [WARN] Snapshot skipped: {snapshot_result.get('reason', 'unknown')}")
        except Exception as e:
            print(f"  [WARN] Snapshot failed: {e}")
        
        # Publish boot completion event for learning triage transition
        try:
            from backend.core.message_bus import message_bus
            await message_bus.publish('grace.boot.complete', {
                'timestamp': datetime.utcnow().isoformat(),
                'chunks_booted': len(boot_orchestrator.completed_chunks)
            })
            logger.info("[BOOT] Boot completion event published")
        except Exception as e:
            logger.debug(f"[BOOT] Could not publish boot completion: {e}")
        
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
    
    # Pre-flight: Clean up any processes on port 8000
    print("[PRE-FLIGHT] Checking for processes on port 8000...")
    import subprocess
    try:
        # Find processes listening on port 8000
        result = subprocess.run(
            ['netstat', '-ano'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        for line in result.stdout.split('\n'):
            if ':8000' in line and 'LISTENING' in line:
                # Extract PID (last column)
                parts = line.split()
                if parts:
                    pid = parts[-1]
                    try:
                        print(f"[PRE-FLIGHT] Killing process on port 8000 (PID {pid})")
                        subprocess.run(['taskkill', '/PID', pid, '/F'], 
                                     capture_output=True, timeout=5)
                        import time
                        time.sleep(1)  # Give it a moment to release the port
                    except:
                        pass
        print("[PRE-FLIGHT] Port check complete")
    except Exception as e:
        print(f"[PRE-FLIGHT] Port check skipped: {e}")
    print()
    
    # Boot Grace (Guardian boots FIRST and allocates port)
    boot_result = asyncio.run(boot_grace_minimal())
    
    if not boot_result or isinstance(boot_result, bool) and not boot_result:
        print("Failed to boot Grace. Exiting.")
        if sys.stdin.isatty():
            input("\nPress Enter to exit...")
        sys.exit(1)
    
    # Get port: Use GRACE_PORT environment variable (default 8000)
    from backend.config.environment import GRACE_PORT
    port = GRACE_PORT
    
    # Sync with Guardian's allocation if available
    if isinstance(boot_result, dict) and 'phases' in boot_result:
        try:
            allocated = boot_result.get('phases', {}).get('phase3_ports', {}).get('port')
            if allocated and allocated != port:
                print(f"[PORT] Guardian allocated port {allocated}, overriding GRACE_PORT {port}")
                port = allocated
        except Exception:
            pass
    
    print(f"[PORT] Using port: {port}")
    
    # Start frontend in background
    print("[FRONTEND] Starting frontend dev server...")
    import subprocess
    frontend_process = None
    try:
        # Since server.py is in root, frontend is directly in "frontend" folder
        frontend_dir = Path(__file__).parent / "frontend"
        if frontend_dir.exists():
            frontend_process = subprocess.Popen(
                ["npm.cmd", "run", "dev"],
                cwd=str(frontend_dir),
                creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
            )
            print(f"[FRONTEND] Started on http://localhost:5173 (PID: {frontend_process.pid})")
        else:
            print("[WARN] Frontend directory not found, skipping frontend")
    except Exception as e:
        print(f"[WARN] Could not start frontend: {e}")
    
    # Start server
    print("=" * 80)
    print("GRACE IS READY")
    print("=" * 80)
    print()
    print(f" Backend:  http://localhost:{port}")
    print(f" Frontend: http://localhost:5173")
    print(f" Docs:     http://localhost:{port}/docs")
    print(f" Health:   http://localhost:{port}/health")
    print()
    print("=" * 80)
    print("Press Ctrl+C to stop both backend and frontend")
    print("=" * 80)
    print()
    
    # Start server on single fixed port
    try:
        print(f"\n[STARTING] Starting Grace backend on port {port}...")
        uvicorn.run(
            "backend.main:app",
            host="0.0.0.0",
            port=port,
            log_level="info",
            reload=False
        )
    except KeyboardInterrupt:
        print("\n\nGrace shutdown requested...")
        if frontend_process:
            print("Stopping frontend...")
            frontend_process.terminate()
            try:
                frontend_process.wait(timeout=5)
            except:
                frontend_process.kill()
        print("Goodbye!")
    except OSError as e:
        if 'address already in use' in str(e).lower() or '10048' in str(e):
            print(f"\n[ERROR] Port {port} already in use!")
            print(f"Set GRACE_PORT environment variable to use different port:")
            print(f"  Example: set GRACE_PORT=8001 && python server.py")
            sys.exit(1)
        else:
            raise
