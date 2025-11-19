"""
Quick test of enhanced chat endpoint
"""

import asyncio
import sys

async def test_chat_service():
    """Test chat service components"""
    print("Testing chat service...")
    
    from backend.services.chat_service import (
        ChatHistoryManager,
        ActionRegistry,
        determine_governance_tier
    )
    
    # Test history manager
    history = ChatHistoryManager()
    history.add_message("session1", "user", "Hello Grace")
    history.add_message("session1", "assistant", "Hello! How can I help?")
    
    messages = history.get_history("session1")
    assert len(messages) == 2
    print(f"[OK] History manager: {len(messages)} messages")
    
    # Test action registry
    registry = ActionRegistry()
    
    # Low-risk action
    action1 = registry.register_action(
        action_type="search",
        agent="grace",
        params={"query": "test"},
        trace_id="trace-1",
        governance_tier="auto_approve"
    )
    assert action1["approved"] == True
    print(f"[OK] Auto-approve action: {action1['action_type']}")
    
    # High-risk action
    action2 = registry.register_action(
        action_type="file_delete",
        agent="grace",
        params={"path": "/tmp/test.txt"},
        trace_id="trace-2",
        governance_tier="user_approval"
    )
    assert action2["approved"] == False
    print(f"[OK] User-approval action: {action2['action_type']}")
    
    # Check pending
    pending = registry.get_pending_approvals()
    assert len(pending) == 1
    print(f"[OK] Pending approvals: {len(pending)}")
    
    # Test governance tiers
    assert determine_governance_tier("search") == "auto_approve"
    assert determine_governance_tier("file_delete") == "user_approval"
    assert determine_governance_tier("system_command") == "user_approval"
    print("[OK] Governance tier determination")
    
    print("\n[SUCCESS] All chat service tests passed!")
    return True

if __name__ == "__main__":
    try:
        asyncio.run(test_chat_service())
    except Exception as e:
        print(f"\n[FAILED] Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
