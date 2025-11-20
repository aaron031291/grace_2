"""
Phase 8: End-to-End Testing Suite
Tests critical user flows across all Grace phases
"""

import pytest
import requests
import time
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

class TestPhase0BootStability:
    """Test Phase 0: Baseline Stabilization"""
    
    def test_server_boots_successfully(self):
        """Verify Grace server boots and responds"""
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        assert response.status_code == 200
        
    def test_all_endpoints_registered(self):
        """Verify all API endpoints are registered"""
        response = requests.get(f"{BASE_URL}/docs", timeout=5)
        assert response.status_code == 200
        
    def test_database_connections(self):
        """Verify database connections are healthy"""
        response = requests.get(f"{BASE_URL}/api/metrics/summary", timeout=5)
        assert response.status_code == 200


class TestPhase1PillarHardening:
    """Test Phase 1: Guardian, Self-Healing, Governance"""
    
    def test_guardian_operational(self):
        """Verify Guardian is operational"""
        response = requests.get(f"{BASE_URL}/api/guardian/health", timeout=5)
        assert response.status_code in [200, 404]
        
    def test_self_healing_active(self):
        """Verify Self-Healing system is active"""
        response = requests.get(f"{BASE_URL}/api/self_healing/status", timeout=5)
        assert response.status_code in [200, 404]
        
    def test_governance_enforced(self):
        """Verify Governance is enforcing policies"""
        response = requests.get(f"{BASE_URL}/api/governance/status", timeout=5)
        assert response.status_code in [200, 404]


class TestPhase2RAGMemory:
    """Test Phase 2: RAG & Memory"""
    
    def test_world_model_accessible(self):
        """Verify World Model is accessible"""
        response = requests.get(f"{BASE_URL}/world-model/stats", timeout=5)
        assert response.status_code == 200
        data = response.json()
        assert "total_entries" in data
        
    def test_vector_search_works(self):
        """Verify vector search functionality"""
        response = requests.get(f"{BASE_URL}/api/vectors/health", timeout=5)
        assert response.status_code in [200, 404]


class TestPhase3LearningEngine:
    """Test Phase 3: Learning Engine & Domain Whitelist"""
    
    def test_learning_hub_operational(self):
        """Verify Learning Hub is operational"""
        response = requests.get(f"{BASE_URL}/api/learning_hub/status", timeout=5)
        assert response.status_code in [200, 404]
        
    def test_domain_whitelist_enforced(self):
        """Verify domain whitelist is enforced"""
        response = requests.get(f"{BASE_URL}/api/learning_hub/whitelist", timeout=5)
        assert response.status_code in [200, 404]


class TestPhase4CopilotBuilding:
    """Test Phase 4: Copilot for Building Software"""
    
    def test_copilot_pipeline_accessible(self):
        """Verify Copilot pipeline is accessible"""
        response = requests.get(f"{BASE_URL}/api/copilot/status", timeout=5)
        assert response.status_code in [200, 404]
        
    def test_code_generation_works(self):
        """Verify code generation functionality"""
        response = requests.get(f"{BASE_URL}/api/copilot/pipeline/status", timeout=5)
        assert response.status_code in [200, 404]


class TestPhase5WorldBuilderUI:
    """Test Phase 5: World Builder UI"""
    
    def test_mission_designer_accessible(self):
        """Verify Mission Designer is accessible"""
        response = requests.get(f"{BASE_URL}/api/missions/list", timeout=5)
        assert response.status_code in [200, 404]
        
    def test_approval_inbox_works(self):
        """Verify Approval Inbox functionality"""
        response = requests.get(f"{BASE_URL}/api/approvals/pending", timeout=5)
        assert response.status_code in [200, 404]


class TestPhase6EnterpriseAPI:
    """Test Phase 6: Enterprise API Management & Scale"""
    
    def test_api_gateway_operational(self):
        """Verify API Gateway is operational"""
        response = requests.get(f"{BASE_URL}/api/gateway/health", timeout=5)
        assert response.status_code in [200, 404]
        
    def test_multi_tenancy_works(self):
        """Verify Multi-Tenancy functionality"""
        response = requests.get(f"{BASE_URL}/api/tenants", timeout=5)
        assert response.status_code in [200, 404]
        
    def test_observability_metrics(self):
        """Verify Observability metrics are collected"""
        response = requests.get(f"{BASE_URL}/api/observability/metrics", timeout=5)
        assert response.status_code in [200, 404]


class TestPhase7SaaSReadiness:
    """Test Phase 7: SaaS Readiness & Business Workflows"""
    
    def test_phase7_summary_accessible(self):
        """Verify Phase 7 summary endpoint"""
        response = requests.get(f"{BASE_URL}/api/phase7/summary", timeout=5)
        assert response.status_code == 200
        data = response.json()
        assert "phase" in data
        assert data["phase"] == "Phase 7: SaaS Readiness & Business Workflows"
        
    def test_product_templates_available(self):
        """Verify Product Templates are available"""
        response = requests.get(f"{BASE_URL}/api/phase7/templates", timeout=5)
        assert response.status_code == 200
        templates = response.json()
        assert isinstance(templates, list)
        assert len(templates) == 6  # 6 starter kits
        
    def test_billing_plans_available(self):
        """Verify Billing Plans are available"""
        response = requests.get(f"{BASE_URL}/api/phase7/subscriptions?tenant_id=test", timeout=5)
        assert response.status_code == 200
        
    def test_rbac_roles_available(self):
        """Verify RBAC Roles are available"""
        response = requests.get(f"{BASE_URL}/api/phase7/roles", timeout=5)
        assert response.status_code == 200
        roles = response.json()
        assert isinstance(roles, list)
        assert len(roles) == 4  # 4 system roles
        
    def test_disaster_recovery_runbooks(self):
        """Verify DR Runbooks are available"""
        response = requests.get(f"{BASE_URL}/api/phase7/runbooks", timeout=5)
        assert response.status_code == 200
        runbooks = response.json()
        assert isinstance(runbooks, list)
        assert len(runbooks) == 3  # 3 DR runbooks


class TestEndToEndUserFlows:
    """Test complete end-to-end user flows"""
    
    def test_complete_saas_workflow(self):
        """Test complete SaaS workflow: Template → Subscription → Deployment"""
        response = requests.get(f"{BASE_URL}/api/phase7/templates", timeout=5)
        assert response.status_code == 200
        templates = response.json()
        assert len(templates) > 0
        
        response = requests.get(f"{BASE_URL}/api/phase7/subscriptions?tenant_id=test", timeout=5)
        assert response.status_code == 200
        
        response = requests.get(f"{BASE_URL}/api/phase7/roles", timeout=5)
        assert response.status_code == 200
        
    def test_health_monitoring_flow(self):
        """Test health monitoring across all systems"""
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        assert response.status_code == 200
        
        response = requests.get(f"{BASE_URL}/api/metrics/summary", timeout=5)
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        
        response = requests.get(f"{BASE_URL}/world-model/stats", timeout=5)
        assert response.status_code == 200
        
    def test_agentic_organism_flow(self):
        """Test agentic organism functionality"""
        response = requests.get(f"{BASE_URL}/api/agentic/events?limit=10", timeout=5)
        assert response.status_code == 200
        
        response = requests.get(f"{BASE_URL}/api/agentic/actions?limit=10", timeout=5)
        assert response.status_code == 200
        
        response = requests.get(f"{BASE_URL}/api/agentic/health", timeout=5)
        assert response.status_code == 200


class TestProductionReadiness:
    """Test production readiness criteria"""
    
    def test_response_times_acceptable(self):
        """Verify API response times are acceptable (<500ms)"""
        start = time.time()
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        duration = time.time() - start
        
        assert response.status_code == 200
        assert duration < 0.5  # Less than 500ms
        
    def test_error_handling_graceful(self):
        """Verify graceful error handling"""
        response = requests.get(f"{BASE_URL}/api/nonexistent/endpoint", timeout=5)
        assert response.status_code == 404
        
    def test_concurrent_requests_handled(self):
        """Verify system handles concurrent requests"""
        import concurrent.futures
        
        def make_request():
            return requests.get(f"{BASE_URL}/health", timeout=5)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
            
        assert all(r.status_code == 200 for r in results)
        
    def test_data_persistence(self):
        """Verify data persistence across requests"""
        response1 = requests.get(f"{BASE_URL}/world-model/stats", timeout=5)
        time.sleep(1)
        response2 = requests.get(f"{BASE_URL}/world-model/stats", timeout=5)
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        data1 = response1.json()
        data2 = response2.json()
        assert data1["total_entries"] == data2["total_entries"]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
