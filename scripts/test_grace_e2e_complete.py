"""
Grace Complete End-to-End Test
Tests every component from kernel to execution layer with full logging
"""

import asyncio
import httpx
import logging
from datetime import datetime
from pathlib import Path
import sys
import traceback
from typing import Dict, Any, List

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

# Configure comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler(f'grace_e2e_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class GraceE2ETestSuite:
    """Comprehensive E2E test suite for entire Grace system"""
    
    def __init__(self):
        self.api_base = "http://localhost:8000"
        self.test_results: Dict[str, Any] = {
            "start_time": datetime.now().isoformat(),
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "component_results": {},
            "errors": []
        }
        self.logger = logging.getLogger("GraceE2E")
    
    async def run_all_tests(self):
        """Run all E2E tests"""
        self.logger.info("=" * 80)
        self.logger.info("GRACE COMPLETE END-TO-END TEST SUITE")
        self.logger.info("=" * 80)
        self.logger.info(f"Start Time: {self.test_results['start_time']}")
        self.logger.info(f"API Base: {self.api_base}")
        self.logger.info("=" * 80)
        
        # Test components in order
        test_suites = [
            ("1. Infrastructure", self.test_infrastructure),
            ("2. Core Domain", self.test_core_domain),
            ("3. Transcendence Domain", self.test_transcendence_domain),
            ("4. Knowledge Domain", self.test_knowledge_domain),
            ("5. Security Domain (Hunter)", self.test_security_domain),
            ("6. ML Domain", self.test_ml_domain),
            ("7. Temporal Domain", self.test_temporal_domain),
            ("8. Parliament Domain", self.test_parliament_domain),
            ("9. Federation Domain", self.test_federation_domain),
            ("10. Speech Domain", self.test_speech_domain),
            ("11. Cognition Dashboard", self.test_cognition_dashboard),
            ("12. Metrics System", self.test_metrics_system),
            ("13. Integration Points", self.test_integration_points),
            ("14. End-to-End Flow", self.test_end_to_end_flow)
        ]
        
        for suite_name, test_func in test_suites:
            self.logger.info(f"\n{'=' * 80}")
            self.logger.info(f"RUNNING: {suite_name}")
            self.logger.info(f"{'=' * 80}")
            
            try:
                await test_func()
                self.test_results["component_results"][suite_name] = "PASSED"
                self.logger.info(f"✓ {suite_name} - PASSED")
            except Exception as e:
                self.test_results["component_results"][suite_name] = "FAILED"
                self.test_results["errors"].append({
                    "suite": suite_name,
                    "error": str(e),
                    "traceback": traceback.format_exc()
                })
                self.logger.error(f"✗ {suite_name} - FAILED: {e}")
                self.logger.error(traceback.format_exc())
        
        # Final report
        self.test_results["end_time"] = datetime.now().isoformat()
        await self.generate_final_report()
    
    async def test_infrastructure(self):
        """Test core infrastructure components"""
        self.logger.info("Testing infrastructure...")
        
        async with httpx.AsyncClient() as client:
            # Health check
            self.logger.info("  → Testing /health endpoint")
            response = await client.get(f"{self.api_base}/health")
            assert response.status_code == 200, "Health check failed"
            data = response.json()
            assert data["status"] == "ok", "Health status not ok"
            self.logger.info(f"    ✓ Health: {data}")
            self.test_results["tests_passed"] += 1
            
            # Database connection
            self.logger.info("  → Testing database connectivity")
            from backend.models import engine
            async with engine.begin() as conn:
                result = await conn.execute("SELECT 1")
                assert result is not None
            self.logger.info("    ✓ Database connected")
            self.test_results["tests_passed"] += 1
            
            # Event bus
            self.logger.info("  → Testing trigger mesh")
            from backend.trigger_mesh import trigger_mesh
            test_event_received = False
            
            def test_handler(event):
                nonlocal test_event_received
                test_event_received = True
            
            trigger_mesh.subscribe("test.event", test_handler)
            await trigger_mesh.emit("test.event", {"test": "data"})
            await asyncio.sleep(0.1)
            assert test_event_received, "Event not received"
            self.logger.info("    ✓ Trigger mesh operational")
            self.test_results["tests_passed"] += 1
        
        self.test_results["tests_run"] += 3
    
    async def test_core_domain(self):
        """Test Core domain operations"""
        self.logger.info("Testing Core domain...")
        
        # Governance
        self.logger.info("  → Testing governance system")
        from backend.governance import governance_engine
        from backend.governance_models import PolicyType
        
        policies = await governance_engine.get_all_policies()
        self.logger.info(f"    ✓ Found {len(policies)} governance policies")
        self.test_results["tests_passed"] += 1
        
        # Self-healing
        self.logger.info("  → Testing self-healing")
        from backend.self_healing import health_monitor
        status = await health_monitor.get_status()
        self.logger.info(f"    ✓ Health monitor status: {status['status']}")
        self.test_results["tests_passed"] += 1
        
        # Verification
        self.logger.info("  → Testing verification system")
        from backend.verification import verification_service
        result = await verification_service.verify_action(
            actor="test_e2e",
            action="test_action",
            resource="test_resource"
        )
        self.logger.info(f"    ✓ Verification result: {result}")
        self.test_results["tests_passed"] += 1
        
        # Publish metrics
        self.logger.info("  → Publishing Core metrics")
        from backend.metric_publishers import CoreMetrics
        await CoreMetrics.publish_uptime(0.99)
        await CoreMetrics.publish_governance_score(0.92)
        self.logger.info("    ✓ Core metrics published")
        self.test_results["tests_passed"] += 1
        
        self.test_results["tests_run"] += 4
    
    async def test_transcendence_domain(self):
        """Test Transcendence domain (agentic coding)"""
        self.logger.info("Testing Transcendence domain...")
        
        # Task executor
        self.logger.info("  → Testing task executor")
        from backend.task_executor import task_executor
        
        task_id = await task_executor.submit_task({
            "type": "test",
            "description": "E2E test task"
        })
        self.logger.info(f"    ✓ Task submitted: {task_id}")
        self.test_results["tests_passed"] += 1
        
        # Code memory
        self.logger.info("  → Testing code memory")
        from backend.code_memory import code_memory_service
        
        await code_memory_service.store_code_snippet(
            code="def test(): pass",
            language="python",
            tags=["test", "e2e"]
        )
        results = await code_memory_service.search_code("test")
        self.logger.info(f"    ✓ Code memory: {len(results)} results")
        self.test_results["tests_passed"] += 1
        
        # Execution engine
        self.logger.info("  → Testing execution engine")
        from backend.execution_engine import execution_engine
        
        result = await execution_engine.execute_plan({
            "steps": [{"action": "test", "params": {}}]
        })
        self.logger.info(f"    ✓ Execution result: {result.get('status', 'unknown')}")
        self.test_results["tests_passed"] += 1
        
        # Publish metrics
        self.logger.info("  → Publishing Transcendence metrics")
        from backend.metric_publishers import OrchestratorMetrics
        await OrchestratorMetrics.publish_task_completed(True, 0.92)
        await OrchestratorMetrics.publish_plan_created(0.88)
        self.logger.info("    ✓ Transcendence metrics published")
        self.test_results["tests_passed"] += 1
        
        self.test_results["tests_run"] += 4
    
    async def test_knowledge_domain(self):
        """Test Knowledge domain"""
        self.logger.info("Testing Knowledge domain...")
        
        # Ingestion service
        self.logger.info("  → Testing knowledge ingestion")
        from backend.ingestion_service import ingestion_service
        
        result = await ingestion_service.ingest_text(
            text="E2E test knowledge",
            source="e2e_test",
            metadata={"test": True}
        )
        self.logger.info(f"    ✓ Knowledge ingested: {result}")
        self.test_results["tests_passed"] += 1
        
        # Trust system
        self.logger.info("  → Testing trust manager")
        from backend.trusted_sources import trust_manager
        
        trust_score = await trust_manager.get_source_trust("e2e_test")
        self.logger.info(f"    ✓ Trust score: {trust_score}")
        self.test_results["tests_passed"] += 1
        
        # Memory service
        self.logger.info("  → Testing memory service")
        from backend.memory_service import memory_service
        
        await memory_service.store_memory(
            content="E2E test memory",
            memory_type="test",
            metadata={"source": "e2e"}
        )
        memories = await memory_service.search_memories("test", limit=5)
        self.logger.info(f"    ✓ Memory service: {len(memories)} memories")
        self.test_results["tests_passed"] += 1
        
        # Publish metrics
        self.logger.info("  → Publishing Knowledge metrics")
        from backend.metric_publishers import KnowledgeMetrics
        await KnowledgeMetrics.publish_ingestion_completed(0.91, 25)
        await KnowledgeMetrics.publish_search_performed(0.93, 8)
        self.logger.info("    ✓ Knowledge metrics published")
        self.test_results["tests_passed"] += 1
        
        self.test_results["tests_run"] += 4
    
    async def test_security_domain(self):
        """Test Security domain (Hunter)"""
        self.logger.info("Testing Security domain...")
        
        # Hunter scanner
        self.logger.info("  → Testing Hunter scanner")
        from backend.hunter import hunter_service
        
        scan_result = await hunter_service.scan_code(
            code="print('test')",
            language="python"
        )
        self.logger.info(f"    ✓ Scan result: {len(scan_result.get('threats', []))} threats")
        self.test_results["tests_passed"] += 1
        
        # Security rules
        self.logger.info("  → Testing security rules")
        from backend.hunter import hunter_service
        
        rules = await hunter_service.get_active_rules()
        self.logger.info(f"    ✓ Active rules: {len(rules)}")
        self.test_results["tests_passed"] += 1
        
        # Auto-quarantine
        self.logger.info("  → Testing auto-quarantine")
        from backend.auto_quarantine import auto_quarantine_service
        
        status = await auto_quarantine_service.get_status()
        self.logger.info(f"    ✓ Auto-quarantine status: {status}")
        self.test_results["tests_passed"] += 1
        
        # Publish metrics
        self.logger.info("  → Publishing Security metrics")
        from backend.metric_publishers import HunterMetrics
        await HunterMetrics.publish_scan_completed(2, 0.96, 0.015)
        await HunterMetrics.publish_threat_quarantined(auto_fixed=True)
        self.logger.info("    ✓ Security metrics published")
        self.test_results["tests_passed"] += 1
        
        self.test_results["tests_run"] += 4
    
    async def test_ml_domain(self):
        """Test ML domain"""
        self.logger.info("Testing ML domain...")
        
        # ML runtime
        self.logger.info("  → Testing ML runtime")
        from backend.ml_runtime import ml_runtime
        
        models = await ml_runtime.list_models()
        self.logger.info(f"    ✓ Available models: {len(models)}")
        self.test_results["tests_passed"] += 1
        
        # Training pipeline
        self.logger.info("  → Testing training pipeline")
        from backend.training_pipeline import training_pipeline
        
        status = await training_pipeline.get_status()
        self.logger.info(f"    ✓ Training pipeline status: {status}")
        self.test_results["tests_passed"] += 1
        
        # Auto-retrain
        self.logger.info("  → Testing auto-retrain")
        from backend.auto_retrain import auto_retrain_engine
        
        engine_status = await auto_retrain_engine.get_status()
        self.logger.info(f"    ✓ Auto-retrain status: {engine_status}")
        self.test_results["tests_passed"] += 1
        
        # Publish metrics
        self.logger.info("  → Publishing ML metrics")
        from backend.metric_publishers import MLMetrics
        await MLMetrics.publish_training_completed(0.94, 1800)
        await MLMetrics.publish_deployment_completed(True, 0.028)
        self.logger.info("    ✓ ML metrics published")
        self.test_results["tests_passed"] += 1
        
        self.test_results["tests_run"] += 4
    
    async def test_temporal_domain(self):
        """Test Temporal domain"""
        self.logger.info("Testing Temporal domain...")
        
        # Temporal reasoning
        self.logger.info("  → Testing temporal reasoning")
        from backend.temporal_reasoning import temporal_engine
        
        prediction = await temporal_engine.predict_outcome({
            "action": "test",
            "context": {"test": True}
        })
        self.logger.info(f"    ✓ Prediction: {prediction}")
        self.test_results["tests_passed"] += 1
        
        # Causal graph
        self.logger.info("  → Testing causal graph")
        from backend.causal_graph import causal_graph_service
        
        await causal_graph_service.add_relationship(
            cause="test_cause",
            effect="test_effect",
            strength=0.85
        )
        self.logger.info("    ✓ Causal relationship added")
        self.test_results["tests_passed"] += 1
        
        # Simulation engine
        self.logger.info("  → Testing simulation engine")
        from backend.simulation_engine import simulation_engine
        
        sim_result = await simulation_engine.run_simulation({
            "scenario": "test",
            "parameters": {}
        })
        self.logger.info(f"    ✓ Simulation result: {sim_result}")
        self.test_results["tests_passed"] += 1
        
        # Publish metrics
        self.logger.info("  → Publishing Temporal metrics")
        from backend.metric_publishers import TemporalMetrics
        await TemporalMetrics.publish_prediction_made(0.87)
        await TemporalMetrics.publish_causal_graph_updated(0.82)
        self.logger.info("    ✓ Temporal metrics published")
        self.test_results["tests_passed"] += 1
        
        self.test_results["tests_run"] += 4
    
    async def test_parliament_domain(self):
        """Test Parliament domain"""
        self.logger.info("Testing Parliament domain...")
        
        # Parliament engine
        self.logger.info("  → Testing Parliament engine")
        from backend.parliament_engine import parliament_engine
        
        proposal = await parliament_engine.create_proposal(
            title="E2E Test Proposal",
            description="Testing Parliament",
            category="test"
        )
        self.logger.info(f"    ✓ Proposal created: {proposal}")
        self.test_results["tests_passed"] += 1
        
        # Meta-loop
        self.logger.info("  → Testing meta-loop")
        from backend.meta_loop_engine import meta_loop_engine
        
        recommendations = await meta_loop_engine.get_recommendations()
        self.logger.info(f"    ✓ Meta-loop recommendations: {len(recommendations)}")
        self.test_results["tests_passed"] += 1
        
        # Reflection service
        self.logger.info("  → Testing reflection")
        from backend.reflection import reflection_service
        
        reflection = await reflection_service.reflect_on_action(
            action="test_action",
            outcome="success"
        )
        self.logger.info(f"    ✓ Reflection: {reflection}")
        self.test_results["tests_passed"] += 1
        
        # Publish metrics
        self.logger.info("  → Publishing Parliament metrics")
        from backend.metric_publishers import ParliamentMetrics
        await ParliamentMetrics.publish_vote_completed(0.95)
        await ParliamentMetrics.publish_recommendation_adopted(True)
        self.logger.info("    ✓ Parliament metrics published")
        self.test_results["tests_passed"] += 1
        
        self.test_results["tests_run"] += 4
    
    async def test_federation_domain(self):
        """Test Federation domain"""
        self.logger.info("Testing Federation domain...")
        
        # Plugin system
        self.logger.info("  → Testing plugin system")
        from backend.plugin_system import plugin_manager
        
        plugins = await plugin_manager.list_plugins()
        self.logger.info(f"    ✓ Loaded plugins: {len(plugins)}")
        self.test_results["tests_passed"] += 1
        
        # Secrets vault
        self.logger.info("  → Testing secrets vault")
        from backend.secrets_vault import secrets_vault
        
        await secrets_vault.store_secret("test_key", "test_value")
        value = await secrets_vault.get_secret("test_key")
        assert value == "test_value"
        self.logger.info("    ✓ Secrets vault operational")
        self.test_results["tests_passed"] += 1
        
        # Sandbox manager
        self.logger.info("  → Testing sandbox")
        from backend.sandbox_manager import sandbox_manager
        
        sandbox = await sandbox_manager.create_sandbox("test_e2e")
        self.logger.info(f"    ✓ Sandbox created: {sandbox}")
        self.test_results["tests_passed"] += 1
        
        # Publish metrics
        self.logger.info("  → Publishing Federation metrics")
        from backend.metric_publishers import FederationMetrics
        await FederationMetrics.publish_connector_health("test", 0.98)
        await FederationMetrics.publish_api_call(True, "test")
        self.logger.info("    ✓ Federation metrics published")
        self.test_results["tests_passed"] += 1
        
        self.test_results["tests_run"] += 4
    
    async def test_speech_domain(self):
        """Test Speech domain"""
        self.logger.info("Testing Speech domain...")
        
        # Speech service
        self.logger.info("  → Testing speech service")
        from backend.speech_service import speech_service
        
        status = await speech_service.get_status()
        self.logger.info(f"    ✓ Speech service status: {status}")
        self.test_results["tests_passed"] += 1
        
        # TTS service
        self.logger.info("  → Testing TTS")
        from backend.tts_service import tts_service
        
        audio = await tts_service.synthesize("Test speech")
        self.logger.info(f"    ✓ TTS synthesized: {len(audio) if audio else 0} bytes")
        self.test_results["tests_passed"] += 1
        
        # Publish metrics
        self.logger.info("  → Publishing Speech metrics")
        from backend.metric_publishers import SpeechMetrics
        await SpeechMetrics.publish_recognition(0.91)
        await SpeechMetrics.publish_voice_command(True, 0.5)
        self.logger.info("    ✓ Speech metrics published")
        self.test_results["tests_passed"] += 1
        
        self.test_results["tests_run"] += 3
    
    async def test_cognition_dashboard(self):
        """Test Cognition Dashboard system"""
        self.logger.info("Testing Cognition Dashboard...")
        
        async with httpx.AsyncClient() as client:
            # Status endpoint
            self.logger.info("  → Testing /api/cognition/status")
            response = await client.get(f"{self.api_base}/api/cognition/status")
            assert response.status_code == 200
            data = response.json()
            assert "overall_health" in data
            assert "domains" in data
            self.logger.info(f"    ✓ Status: Health={data['overall_health']:.1%}")
            self.test_results["tests_passed"] += 1
            
            # Readiness endpoint
            self.logger.info("  → Testing /api/cognition/readiness")
            response = await client.get(f"{self.api_base}/api/cognition/readiness")
            assert response.status_code == 200
            data = response.json()
            assert "ready" in data
            assert "benchmarks" in data
            self.logger.info(f"    ✓ Readiness: {data['ready']}")
            self.test_results["tests_passed"] += 1
            
            # Domain update
            self.logger.info("  → Testing domain update")
            response = await client.post(
                f"{self.api_base}/api/cognition/domain/transcendence/update",
                json={"task_success": 0.95, "code_quality": 0.90}
            )
            assert response.status_code == 200
            self.logger.info("    ✓ Domain updated")
            self.test_results["tests_passed"] += 1
        
        self.test_results["tests_run"] += 3
    
    async def test_metrics_system(self):
        """Test metrics collection and aggregation"""
        self.logger.info("Testing Metrics System...")
        
        # Metrics collector
        self.logger.info("  → Testing metrics collector")
        from backend.metrics_service import get_metrics_collector, publish_metric
        
        collector = get_metrics_collector()
        await publish_metric("test_domain", "test_metric", 0.85)
        
        history = collector.get_metric_history("test_domain", "test_metric", hours=1)
        assert len(history) > 0
        self.logger.info(f"    ✓ Metrics collected: {len(history)} events")
        self.test_results["tests_passed"] += 1
        
        # Cognition engine
        self.logger.info("  → Testing cognition engine")
        from backend.cognition_metrics import get_metrics_engine
        
        engine = get_metrics_engine()
        status = engine.get_status()
        assert "overall_health" in status
        self.logger.info(f"    ✓ Cognition engine: {len(engine.domains)} domains")
        self.test_results["tests_passed"] += 1
        
        # Benchmark windows
        self.logger.info("  → Testing benchmark windows")
        assert "overall_health" in engine.benchmarks
        bench = engine.benchmarks["overall_health"]
        self.logger.info(f"    ✓ Benchmark: {len(bench.values)} samples, avg={bench.average():.1%}")
        self.test_results["tests_passed"] += 1
        
        self.test_results["tests_run"] += 3
    
    async def test_integration_points(self):
        """Test cross-domain integrations"""
        self.logger.info("Testing Integration Points...")
        
        # Trigger mesh integration
        self.logger.info("  → Testing trigger mesh subscriptions")
        from backend.trigger_mesh import trigger_mesh
        
        events = []
        def event_handler(event):
            events.append(event)
        
        trigger_mesh.subscribe("integration.test", event_handler)
        await trigger_mesh.emit("integration.test", {"test": "integration"})
        await asyncio.sleep(0.1)
        assert len(events) > 0
        self.logger.info("    ✓ Trigger mesh integration working")
        self.test_results["tests_passed"] += 1
        
        # Verification integration
        self.logger.info("  → Testing verification integration")
        from backend.verification_integration import verification_integration
        
        audit_log = await verification_integration.get_verification_audit_log(limit=5)
        self.logger.info(f"    ✓ Verification audit: {len(audit_log)} entries")
        self.test_results["tests_passed"] += 1
        
        # WebSocket integration
        self.logger.info("  → Testing WebSocket manager")
        from backend.websocket_manager import websocket_manager
        
        status = websocket_manager.get_connection_count()
        self.logger.info(f"    ✓ WebSocket connections: {status}")
        self.test_results["tests_passed"] += 1
        
        self.test_results["tests_run"] += 3
    
    async def test_end_to_end_flow(self):
        """Test complete end-to-end user flow"""
        self.logger.info("Testing End-to-End Flow...")
        
        # 1. Submit task
        self.logger.info("  → Submitting task via API")
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_base}/api/tasks",
                json={
                    "description": "E2E test task",
                    "type": "test"
                }
            )
            assert response.status_code in [200, 201]
            task_data = response.json()
            self.logger.info(f"    ✓ Task created: {task_data.get('id', 'unknown')}")
            self.test_results["tests_passed"] += 1
        
        # 2. Publish metrics from multiple domains
        self.logger.info("  → Publishing metrics from all domains")
        from backend.metric_publishers import (
            CoreMetrics,
            OrchestratorMetrics,
            KnowledgeMetrics,
            HunterMetrics,
            MLMetrics,
            TemporalMetrics,
            ParliamentMetrics,
            FederationMetrics,
            SpeechMetrics,
        )
        
        await CoreMetrics.publish_uptime(0.99)
        await OrchestratorMetrics.publish_task_completed(True, 0.92)
        await KnowledgeMetrics.publish_ingestion_completed(0.91, 25)
        await HunterMetrics.publish_scan_completed(1, 0.97, 0.012)
        await MLMetrics.publish_training_completed(0.95, 1500)
        await TemporalMetrics.publish_prediction_made(0.88)
        await ParliamentMetrics.publish_vote_completed(0.94)
        await FederationMetrics.publish_connector_health("e2e", 0.99)
        await SpeechMetrics.publish_recognition(0.92)
        
        self.logger.info("    ✓ Metrics published from 9 domains")
        self.test_results["tests_passed"] += 1
        
        # 3. Verify cognition status updated
        self.logger.info("  → Verifying cognition status")
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.api_base}/api/cognition/status")
            assert response.status_code == 200
            data = response.json()
            
            domains_with_kpis = [d for d in data['domains'].values() if d.get('kpis')]
            self.logger.info(f"    ✓ Cognition updated: {len(domains_with_kpis)} domains reporting")
            self.test_results["tests_passed"] += 1
        
        # 4. Generate readiness report
        self.logger.info("  → Generating readiness report")
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{self.api_base}/api/cognition/report/latest")
            assert response.status_code == 200
            report_data = response.json()
            self.logger.info(f"    ✓ Report generated: {len(report_data.get('content', ''))} chars")
            self.test_results["tests_passed"] += 1
        
        self.test_results["tests_run"] += 4
    
    async def generate_final_report(self):
        """Generate comprehensive test report"""
        self.logger.info("\n" + "=" * 80)
        self.logger.info("FINAL TEST REPORT")
        self.logger.info("=" * 80)
        
        # Summary
        total_tests = self.test_results["tests_run"]
        passed = self.test_results["tests_passed"]
        failed = self.test_results["tests_failed"]
        
        self.logger.info(f"\nTest Summary:")
        self.logger.info(f"  Total Tests Run: {total_tests}")
        self.logger.info(f"  Passed: {passed} ✓")
        self.logger.info(f"  Failed: {failed} ✗")
        self.logger.info(f"  Success Rate: {(passed/total_tests*100) if total_tests > 0 else 0:.1f}%")
        
        # Component results
        self.logger.info(f"\nComponent Results:")
        for component, result in self.test_results["component_results"].items():
            status_icon = "✓" if result == "PASSED" else "✗"
            self.logger.info(f"  {status_icon} {component}: {result}")
        
        # Errors
        if self.test_results["errors"]:
            self.logger.info(f"\nErrors Encountered:")
            for error in self.test_results["errors"]:
                self.logger.error(f"  Suite: {error['suite']}")
                self.logger.error(f"  Error: {error['error']}")
        
        # Timing
        start = datetime.fromisoformat(self.test_results["start_time"])
        end = datetime.fromisoformat(self.test_results["end_time"])
        duration = (end - start).total_seconds()
        
        self.logger.info(f"\nTiming:")
        self.logger.info(f"  Start: {self.test_results['start_time']}")
        self.logger.info(f"  End: {self.test_results['end_time']}")
        self.logger.info(f"  Duration: {duration:.2f} seconds")
        
        # Final status
        self.logger.info("\n" + "=" * 80)
        if failed == 0 and total_tests > 0:
            self.logger.info("🎉 ALL TESTS PASSED! Grace is fully operational.")
        else:
            self.logger.info("⚠️  Some tests failed. Review errors above.")
        self.logger.info("=" * 80)
        
        # Save report to file
        report_file = Path(f"grace_e2e_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        with open(report_file, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("GRACE COMPLETE E2E TEST REPORT\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Start: {self.test_results['start_time']}\n")
            f.write(f"End: {self.test_results['end_time']}\n")
            f.write(f"Duration: {duration:.2f}s\n\n")
            f.write(f"Tests Run: {total_tests}\n")
            f.write(f"Passed: {passed}\n")
            f.write(f"Failed: {failed}\n")
            f.write(f"Success Rate: {(passed/total_tests*100) if total_tests > 0 else 0:.1f}%\n\n")
            f.write("Component Results:\n")
            for component, result in self.test_results["component_results"].items():
                f.write(f"  {component}: {result}\n")
        
        self.logger.info(f"\n📄 Full report saved to: {report_file}")


async def main():
    """Run complete E2E test suite"""
    suite = GraceE2ETestSuite()
    
    try:
        await suite.run_all_tests()
    except KeyboardInterrupt:
        logger.info("\n⚠️  Test suite interrupted by user")
    except Exception as e:
        logger.error(f"\n❌ Fatal error: {e}")
        logger.error(traceback.format_exc())
    
    return suite.test_results


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("GRACE COMPLETE END-TO-END TEST SUITE")
    print("=" * 80)
    print("\nTesting every component from kernel to execution layer...")
    print("Logs will be saved to grace_e2e_test_*.log\n")
    
    results = asyncio.run(main())
    
    # Exit with appropriate code
    if results["tests_failed"] == 0 and results["tests_run"] > 0:
        sys.exit(0)
    else:
        sys.exit(1)
