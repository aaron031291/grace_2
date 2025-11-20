# pytest configuration for Grace test suite

import pytest
import sys
from pathlib import Path

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


collect_ignore = [
    # Missing dependencies - future implementation
    "test_grace.py",
    "test_diagnostic.py",
    "test_external_apis.py",
    "test_full_integration.py",
    "test_crypto_persistence.py",
    "test_collaboration_e2e.py",
    "test_knowledge_ingestion.py",
    "test_layer2_hardening.py",
    "test_layer3_integration.py",
    "test_payment_marketplace.py",
    "test_e2e_production_scenario.py",
    "test_agentic_integration.py",
    "test_agentic_spine_integration.py",
    "test_amp_coding_agent.py",
    "test_dashboards.py",
    "test_ide_websocket.py",
    "test_metrics_catalog.py",
    "test_new_systems_integration.py",
    "test_orchestrator_cli.py",
    "test_unified_grace_orchestrator.py",
    "verify_grace.py",
    "stress_test_suite.py",
    "check_tables.py",
    # Subdirectories with integration tests
    "stress/",
    "e2e/",
    "features/",
    "systems/",
    "security/",
    "kernels/",
    "api/",
]


def pytest_ignore_collect(collection_path, config):
    """Skip collection of certain test files and directories."""
    path_str = str(collection_path)
    
    # Check if path matches any ignored patterns
    for pattern in collect_ignore:
        if pattern in path_str:
            return True
    
    return False
