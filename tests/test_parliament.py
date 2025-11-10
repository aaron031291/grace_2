"""Parliament System Tests

Test parliament governance, voting, quorum, and Grace integration.
"""

import pytest
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.parliament_engine import parliament_engine
from backend.grace_parliament_agent import grace_voting_agent
from backend.governance import governance_engine
from backend.models import engine, Base

@pytest.fixture(scope="function")
async def setup_db():
    """Setup test database"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.mark.asyncio
async def test_create_member(setup_db):
    """Test creating a parliament member"""
    
    member = await parliament_engine.create_member(
        member_id="test_user",
        member_type="human",
        display_name="Test User",
        role="member",
        committees=["general"],
        vote_weight=1.0
    )
    
    assert member["member_id"] == "test_user"
    assert member["display_name"] == "Test User"
    assert member["vote_weight"] == 1.0
    print("✓ Member creation test passed")

@pytest.mark.asyncio
async def test_list_members(setup_db):
    """Test listing parliament members"""
    
    # Create multiple members
    await parliament_engine.create_member(
        member_id="user1",
        member_type="human",
        display_name="User One",
        role="member",
        committees=["general"]
    )
    
    await parliament_engine.create_member(
        member_id="user2",
        member_type="agent",
        display_name="Agent Two",
        role="member",
        committees=["security"]
    )
    
    members = await parliament_engine.list_members()
    
    assert len(members) >= 2
    assert any(m["member_id"] == "user1" for m in members)
    assert any(m["member_id"] == "user2" for m in members)
    print("✓ List members test passed")

@pytest.mark.asyncio
async def test_create_session(setup_db):
    """Test creating a voting session"""
    
    session = await parliament_engine.create_session(
        policy_name="test_policy",
        action_type="execute",
        action_payload={"command": "test"},
        actor="test_user",
        category="execution",
        resource="test_resource",
        committee="general",
        quorum_required=2,
        approval_threshold=0.5
    )
    
    assert session["status"] == "voting"
    assert session["committee"] == "general"
    assert session["quorum_required"] == 2
    print("✓ Session creation test passed")

@pytest.mark.asyncio
async def test_voting_with_quorum(setup_db):
    """Test voting process with quorum"""
    
    # Create members
    await parliament_engine.create_member(
        member_id="voter1",
        member_type="human",
        display_name="Voter One",
        role="member",
        committees=["general"]
    )
    
    await parliament_engine.create_member(
        member_id="voter2",
        member_type="human",
        display_name="Voter Two",
        role="member",
        committees=["general"]
    )
    
    await parliament_engine.create_member(
        member_id="voter3",
        member_type="human",
        display_name="Voter Three",
        role="member",
        committees=["general"]
    )
    
    # Create session
    session = await parliament_engine.create_session(
        policy_name="test_vote",
        action_type="approve",
        action_payload={"test": "data"},
        actor="voter1",
        committee="general",
        quorum_required=3,
        approval_threshold=0.5
    )
    
    session_id = session["session_id"]
    
    # Cast votes
    vote1 = await parliament_engine.cast_vote(
        session_id=session_id,
        member_id="voter1",
        vote="approve",
        reason="I approve"
    )
    
    assert vote1["decision"]["status"] == "voting"
    assert vote1["decision"]["votes_needed"] == 2
    
    vote2 = await parliament_engine.cast_vote(
        session_id=session_id,
        member_id="voter2",
        vote="approve",
        reason="I also approve"
    )
    
    assert vote2["decision"]["status"] == "voting"
    assert vote2["decision"]["votes_needed"] == 1
    
    vote3 = await parliament_engine.cast_vote(
        session_id=session_id,
        member_id="voter3",
        vote="approve",
        reason="Me too"
    )
    
    # Should reach quorum and approve (3/3 approve, 100% > 50%)
    assert vote3["decision"]["status"] == "approved"
    assert vote3["decision"]["outcome"] == "approved"
    
    print("✓ Voting with quorum test passed")

@pytest.mark.asyncio
async def test_voting_rejection(setup_db):
    """Test voting rejection when threshold not met"""
    
    # Create members
    for i in range(1, 4):
        await parliament_engine.create_member(
            member_id=f"voter{i}",
            member_type="human",
            display_name=f"Voter {i}",
            role="member",
            committees=["general"]
        )
    
    # Create session
    session = await parliament_engine.create_session(
        policy_name="test_reject",
        action_type="execute",
        action_payload={"test": "data"},
        actor="voter1",
        committee="general",
        quorum_required=3,
        approval_threshold=0.5
    )
    
    session_id = session["session_id"]
    
    # Cast votes: 1 approve, 2 reject
    await parliament_engine.cast_vote(session_id=session_id, member_id="voter1", vote="approve")
    await parliament_engine.cast_vote(session_id=session_id, member_id="voter2", vote="reject")
    vote3 = await parliament_engine.cast_vote(session_id=session_id, member_id="voter3", vote="reject")
    
    # Should reject (1/3 approve, 33% < 50%)
    assert vote3["decision"]["status"] == "rejected"
    assert vote3["decision"]["outcome"] == "rejected"
    
    print("✓ Voting rejection test passed")

@pytest.mark.asyncio
async def test_voting_tie(setup_db):
    """Test voting with all abstentions"""
    
    # Create members
    for i in range(1, 4):
        await parliament_engine.create_member(
            member_id=f"voter{i}",
            member_type="human",
            display_name=f"Voter {i}",
            role="member",
            committees=["general"]
        )
    
    # Create session
    session = await parliament_engine.create_session(
        policy_name="test_tie",
        action_type="execute",
        action_payload={"test": "data"},
        actor="voter1",
        committee="general",
        quorum_required=3,
        approval_threshold=0.5
    )
    
    session_id = session["session_id"]
    
    # All abstain
    await parliament_engine.cast_vote(session_id=session_id, member_id="voter1", vote="abstain")
    await parliament_engine.cast_vote(session_id=session_id, member_id="voter2", vote="abstain")
    vote3 = await parliament_engine.cast_vote(session_id=session_id, member_id="voter3", vote="abstain")
    
    # Should be tie (all abstained)
    assert vote3["decision"]["status"] == "tie"
    assert vote3["decision"]["outcome"] == "tie"
    
    print("✓ Voting tie test passed")

@pytest.mark.asyncio
async def test_grace_automated_voting(setup_db):
    """Test Grace automated voting"""
    
    # Register Grace
    await grace_voting_agent.register()
    
    # Create session with security alert
    session = await parliament_engine.create_session(
        policy_name="security_test",
        action_type="execute",
        action_payload={"command": "rm -rf /"},
        actor="suspicious_user",
        category="security",
        resource="filesystem",
        committee="security",
        quorum_required=2,
        approval_threshold=0.5,
        hunter_alerts=[
            {"severity": "critical", "rule_name": "Dangerous command detected"}
        ],
        risk_level="critical"
    )
    
    session_id = session["session_id"]
    
    # Grace should auto-vote
    result = await grace_voting_agent.cast_automated_vote(session_id)
    
    # Grace should reject due to critical alert
    assert result["analysis"]["vote_recommendation"] == "reject"
    assert result["analysis"]["confidence"] >= 0.9
    assert "critical_security_alerts" in result["analysis"]["factors"]
    
    print("✓ Grace automated voting test passed")

@pytest.mark.asyncio
async def test_grace_monitor_sessions(setup_db):
    """Test Grace monitoring and auto-voting on multiple sessions"""
    
    await grace_voting_agent.register()
    
    # Create another voter so quorum can be met
    await parliament_engine.create_member(
        member_id="human_voter",
        member_type="human",
        display_name="Human Voter",
        role="member",
        committees=["security", "general"]
    )
    
    # Create multiple sessions
    for i in range(3):
        await parliament_engine.create_session(
            policy_name=f"test_policy_{i}",
            action_type="execute",
            action_payload={"test": i},
            actor="test_user",
            committee="general",
            quorum_required=2,
            approval_threshold=0.5
        )
    
    # Monitor and auto-vote
    result = await grace_voting_agent.monitor_sessions(auto_vote=True)
    
    assert result["total_sessions"] == 3
    assert result["voted"] == 3
    assert len(result["votes"]) == 3
    
    print("✓ Grace monitor sessions test passed")

@pytest.mark.asyncio
async def test_governance_integration(setup_db):
    """Test Parliament integration with governance"""
    
    from backend.governance_models import GovernancePolicy
    from backend.models import async_session
    import json
    
    # Create a policy requiring review
    async with async_session() as session:
        policy = GovernancePolicy(
            name="high_risk_execution",
            condition=json.dumps({"action": "execute", "keywords": ["dangerous"]}),
            action="review"
        )
        session.add(policy)
        await session.commit()
    
    # Trigger governance check
    result = await governance_engine.check(
        actor="test_user",
        action="execute",
        resource="system",
        payload={"command": "dangerous operation"}
    )
    
    # Should create parliament session
    assert result["decision"] == "parliament_pending"
    assert "parliament_session_id" in result
    
    # Verify session was created
    session_id = result["parliament_session_id"]
    parliament_session = await parliament_engine.get_session(session_id)
    
    assert parliament_session is not None
    assert parliament_session["policy_name"] == "high_risk_execution"
    assert parliament_session["status"] in ["voting", "approved", "rejected"]
    
    print("✓ Governance integration test passed")

@pytest.mark.asyncio
async def test_committee_creation(setup_db):
    """Test creating committees"""
    
    committee = await parliament_engine.create_committee(
        committee_name="test_committee",
        display_name="Test Committee",
        description="For testing",
        responsibilities=["test"],
        min_members=2,
        max_members=5,
        default_quorum=2,
        default_threshold=0.5
    )
    
    assert committee["committee_name"] == "test_committee"
    assert committee["display_name"] == "Test Committee"
    
    # List committees
    committees = await parliament_engine.list_committees()
    assert any(c["committee_name"] == "test_committee" for c in committees)
    
    print("✓ Committee creation test passed")

@pytest.mark.asyncio
async def test_parliament_statistics(setup_db):
    """Test parliament statistics"""
    
    # Create some data
    await parliament_engine.create_member(
        member_id="stats_user",
        member_type="human",
        display_name="Stats User",
        role="member",
        committees=["general"]
    )
    
    session = await parliament_engine.create_session(
        policy_name="stats_test",
        action_type="execute",
        action_payload={"test": "data"},
        actor="stats_user",
        quorum_required=1
    )
    
    await parliament_engine.cast_vote(
        session_id=session["session_id"],
        member_id="stats_user",
        vote="approve"
    )
    
    # Get stats
    stats = await parliament_engine.get_statistics()
    
    assert stats["total_members"] >= 1
    assert stats["total_sessions"] >= 1
    assert stats["sessions_approved"] >= 1
    
    print("✓ Parliament statistics test passed")

def run_all_tests():
    """Run all tests"""
    print("🏛️ Running Parliament System Tests...\n")
    
    tests = [
        test_create_member,
        test_list_members,
        test_create_session,
        test_voting_with_quorum,
        test_voting_rejection,
        test_voting_tie,
        test_grace_automated_voting,
        test_grace_monitor_sessions,
        test_governance_integration,
        test_committee_creation,
        test_parliament_statistics
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            asyncio.run(test(None))
            passed += 1
        except Exception as e:
            print(f"✗ {test.__name__} failed: {e}")
            failed += 1
    
    print(f"\n{'='*60}")
    print(f"Tests Passed: {passed}/{len(tests)}")
    print(f"Tests Failed: {failed}/{len(tests)}")
    print(f"{'='*60}")
    
    return failed == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
