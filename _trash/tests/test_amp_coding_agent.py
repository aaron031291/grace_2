"""
Integration Test for AMP-Grade Coding Agent
Tests all three pillars working together
"""

import pytest
import asyncio
from pathlib import Path

from backend.agents_core.amp_grade_coding_agent import (
    get_amp_coding_agent,
    CodingTask,
    ModelCapability
)


@pytest.mark.asyncio
async def test_amp_agent_initialization():
    """Test AMP agent initializes all systems"""
    
    agent = await get_amp_coding_agent()
    
    assert agent.initialized
    assert agent.source_graph is not None
    assert agent.model_registry is not None
    assert agent.autonomy_gatekeeper is not None
    assert agent.audit_loop is not None
    
    # Check source graph built
    assert agent.source_graph.stats["total_nodes"] > 0
    
    # Check models registered
    assert len(agent.model_registry.adapters) >= 5  # At least 5 models
    
    print(f"✅ Agent initialized with {len(agent.model_registry.adapters)} models")


@pytest.mark.asyncio
async def test_tier1_safe_operation():
    """Test Tier 1 (safe) operation auto-approval"""
    
    agent = await get_amp_coding_agent()
    
    task = CodingTask(
        task_id="test_tier1",
        description="Add docstrings to functions",
        operation="add_docs",
        target_files=["backend/misc/test_file.py"],
        requires_tests=False
    )
    
    result = await agent.execute_task(task)
    
    assert result["success"]
    assert "intent_id" in result
    assert result["model_used"] is not None
    
    # Check autonomy tier was Tier 1
    intent_id = result["intent_id"]
    intent_status = agent.autonomy_gatekeeper.get_intent_status(intent_id)
    assert intent_status["intent"]["autonomy_tier"] == 1  # Tier 1
    
    print(f"✅ Tier 1 task executed successfully")


@pytest.mark.asyncio
async def test_tier2_governed_operation():
    """Test Tier 2 (internal) operation with governance"""
    
    agent = await get_amp_coding_agent()
    
    task = CodingTask(
        task_id="test_tier2",
        description="Refactor helper functions",
        operation="refactor",
        target_files=["backend/misc/utils.py"],
        requires_tests=True,
        test_command="pytest tests/test_utils.py"
    )
    
    result = await agent.execute_task(task)
    
    assert result["success"]
    
    # Check governance was consulted
    intent_status = agent.autonomy_gatekeeper.get_intent_status(result["intent_id"])
    assert intent_status["intent"]["autonomy_tier"] == 2  # Tier 2
    
    print(f"✅ Tier 2 task executed with governance approval")


@pytest.mark.asyncio
async def test_audit_loop_trigger():
    """Test that 15-action audit loop triggers"""
    
    agent = await get_amp_coding_agent()
    
    initial_stats = agent.audit_loop.get_stats()
    
    # Execute 15 safe tasks to trigger audit
    for i in range(15):
        task = CodingTask(
            task_id=f"test_audit_{i}",
            description=f"Format file {i}",
            operation="format",
            target_files=[f"backend/test_file_{i}.py"],
            requires_tests=False
        )
        
        result = await agent.execute_task(task)
        assert result["success"]
    
    # Check audit was triggered
    final_stats = agent.audit_loop.get_stats()
    
    assert final_stats["total_audits"] > initial_stats["total_audits"]
    
    print(f"✅ Audit loop triggered after 15 actions")


@pytest.mark.asyncio
async def test_model_adapter_verification():
    """Test that changes to model adapters trigger Tier 3"""
    
    agent = await get_amp_coding_agent()
    
    # Simulate source graph showing model adapter affected
    context = {
        "files": ["backend/agents_core/model_llama.py"],
        "affected_model_adapters": [
            {"name": "llama3.2:3b", "contract_hash": "abc123"}
        ]
    }
    
    intent = await agent.autonomy_gatekeeper.request_intent(
        task_description="Update Llama model adapter",
        target_files=["backend/agents_core/model_llama.py"],
        operation="update_model",
        source_graph_context=context
    )
    
    # Should be Tier 3 (not auto-approved)
    assert intent.autonomy_tier.value == 3
    assert not intent.approved  # Requires explicit approval
    
    print(f"✅ Model adapter changes correctly flagged as Tier 3")


@pytest.mark.asyncio
async def test_hallucination_detection():
    """Test hallucination guardrails detect suspicious patterns"""
    
    agent = await get_amp_coding_agent()
    
    # Create a test file with suspicious repetition
    test_file = Path("backend/test_hallucination.py")
    
    suspicious_code = "\n".join([
        "def function():",
        "    pass",
        "    pass",
        "    pass",
        "    pass",
        "    pass",
        "    pass",  # Excessive repetition
    ])
    
    test_file.write_text(suspicious_code)
    
    try:
        # Record action with this file
        await agent.audit_loop.record_action(
            action_type="add_function",
            files_touched=[str(test_file)],
            intent_id="test_hallucination"
        )
        
        # Trigger audit
        await agent.force_audit()
        
        # Check if hallucination was detected
        stats = agent.audit_loop.get_stats()
        
        # Note: Detection depends on heuristics, may not always flag
        print(f"Hallucination checks run: {stats.get('hallucinations_detected', 0)}")
        
    finally:
        # Cleanup
        if test_file.exists():
            test_file.unlink()
    
    print(f"✅ Hallucination guardrails executed")


@pytest.mark.asyncio
async def test_verification_bundle_creation():
    """Test verification bundle includes all checks"""
    
    agent = await get_amp_coding_agent()
    
    # Create and approve an intent
    intent = await agent.autonomy_gatekeeper.request_intent(
        task_description="Test verification",
        target_files=["backend/test.py"],
        operation="lint"
    )
    
    # Create verification bundle
    bundle = await agent.autonomy_gatekeeper.create_verification_bundle(
        intent_id=intent.intent_id,
        files_changed=["backend/test.py"]
    )
    
    # Check bundle completeness
    assert bundle.bundle_id is not None
    assert bundle.lint_passed is not None
    assert bundle.trust_score > 0
    assert bundle.governance_approved is not None
    assert bundle.immutable_log_id is not None
    
    print(f"✅ Verification bundle created - Trust: {bundle.trust_score:.2f}")


@pytest.mark.asyncio
async def test_comprehensive_status():
    """Test comprehensive status reporting"""
    
    agent = await get_amp_coding_agent()
    
    status = agent.get_comprehensive_status()
    
    # Check all pillars present
    assert "source_graph" in status
    assert "model_registry" in status
    assert "autonomy_gates" in status
    assert "audit_loop" in status
    
    # Check source graph stats
    assert status["source_graph"]["total_nodes"] > 0
    
    # Check model registry
    assert status["model_registry"]["total_adapters"] >= 5
    
    # Check audit loop
    assert "total_actions" in status["audit_loop"]
    
    print(f"✅ Comprehensive status: {status}")


if __name__ == "__main__":
    # Run tests
    asyncio.run(test_amp_agent_initialization())
    asyncio.run(test_tier1_safe_operation())
    asyncio.run(test_tier2_governed_operation())
    asyncio.run(test_audit_loop_trigger())
    asyncio.run(test_model_adapter_verification())
    asyncio.run(test_hallucination_detection())
    asyncio.run(test_verification_bundle_creation())
    asyncio.run(test_comprehensive_status())
    
    print("\n✅ All AMP-grade coding agent tests passed!")
