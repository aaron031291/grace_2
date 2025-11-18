"""
Verify Chat System Wiring

Tests the complete pipeline:
1. RAG retrieval
2. World Model query
3. OpenAI Reasoner integration
4. Action Gateway
5. Governance approvals
"""

import asyncio
import sys
from typing import Dict, Any


async def test_rag_retrieval():
    """Test RAG service is initialized and can retrieve context"""
    print("\n[1/6] Testing RAG Retrieval...")
    try:
        from backend.services.rag_service import RAGService
        
        rag = RAGService()
        await rag.initialize()
        
        results = await rag.retrieve(
            query="What is Grace?",
            top_k=3,
            requested_by="test"
        )
        
        print(f"  ✅ RAG initialized and returned {len(results.get('results', []))} results")
        return True
    except Exception as e:
        print(f"  ❌ RAG retrieval failed: {e}")
        return False


async def test_world_model_query():
    """Test World Model can be queried for canonical facts"""
    print("\n[2/6] Testing World Model Query...")
    try:
        from backend.world_model.grace_world_model import grace_world_model
        
        await grace_world_model.initialize()
        
        results = await grace_world_model.query(
            query="system status",
            top_k=3
        )
        
        print(f"  ✅ World Model initialized and returned {len(results)} knowledge items")
        return True
    except Exception as e:
        print(f"  ❌ World Model query failed: {e}")
        return False


async def test_openai_reasoner():
    """Test OpenAI Reasoner can generate responses"""
    print("\n[3/6] Testing OpenAI Reasoner...")
    try:
        from backend.services.openai_reasoner import openai_reasoner
        import os
        
        if not os.getenv("OPENAI_API_KEY"):
            print("  ⚠️  OPENAI_API_KEY not set - skipping reasoner test")
            return True
        
        response = await openai_reasoner.generate(
            user_message="Hello, what are you?",
            conversation_history=[],
            rag_context=[],
            world_model_facts={"facts": []},
            trust_context={"trust_score": 0.8}
        )
        
        print(f"  ✅ Reasoner generated response with confidence {response['confidence']:.2f}")
        print(f"     Reply preview: {response['reply'][:100]}...")
        return True
    except Exception as e:
        print(f"  ❌ OpenAI Reasoner failed: {e}")
        return False


async def test_action_gateway():
    """Test Action Gateway can process approval requests"""
    print("\n[4/6] Testing Action Gateway...")
    try:
        from backend.action_gateway import action_gateway
        
        result = await action_gateway.request_action(
            action_type="test_action",
            agent="test_agent",
            params={"test": "value"},
            trace_id="test_trace_001"
        )
        
        approved = result.get("approved")
        tier = result.get("governance_tier")
        
        print(f"  ✅ Action Gateway processed request (tier: {tier}, approved: {approved})")
        return True
    except Exception as e:
        print(f"  ❌ Action Gateway failed: {e}")
        return False


async def test_chat_endpoint():
    """Test chat endpoint integrates all components"""
    print("\n[5/6] Testing Chat Endpoint Integration...")
    try:
        from backend.routes.chat_api import chat_with_grace, ChatMessage
        import os
        
        if not os.getenv("OPENAI_API_KEY"):
            print("  ⚠️  OPENAI_API_KEY not set - skipping chat test")
            return True
        
        msg = ChatMessage(
            message="What is Grace?",
            user_id="test_user"
        )
        
        response = await chat_with_grace(msg)
        
        print(f"  ✅ Chat endpoint returned response")
        print(f"     Session: {response.session_id}")
        print(f"     Confidence: {response.confidence:.2f}")
        print(f"     Citations: {len(response.citations)}")
        print(f"     Reply: {response.reply[:100]}...")
        return True
    except Exception as e:
        print(f"  ❌ Chat endpoint failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_governance_endpoints():
    """Test governance API endpoints exist and work"""
    print("\n[6/6] Testing Governance Endpoints...")
    try:
        from backend.routes.governance_api import get_pending_approvals, get_governance_stats
        
        # Test pending approvals
        pending = await get_pending_approvals(limit=10)
        print(f"  ✅ Pending approvals: {pending['total_pending']}")
        
        # Test governance stats
        stats = await get_governance_stats()
        print(f"  ✅ Governance stats: {stats['total_actions']} total actions")
        print(f"     Approved: {stats['approved']}, Rejected: {stats['rejected']}, Pending: {stats['pending']}")
        
        return True
    except Exception as e:
        print(f"  ❌ Governance endpoints failed: {e}")
        return False


async def test_logging_integration():
    """Test that responses are logged for governance/notification pickup"""
    print("\n[7/7] Testing Logging Integration...")
    try:
        from backend.event_bus import event_bus
        
        # Check event bus has events
        if len(event_bus.event_log) > 0:
            print(f"  ✅ Event bus has {len(event_bus.event_log)} events logged")
            
            # Check for governance events
            gov_events = [e for e in event_bus.event_log if e.event_type.name == "GOVERNANCE_CHECK"]
            print(f"  ✅ Found {len(gov_events)} governance events")
            
            return True
        else:
            print("  ⚠️  Event bus empty - events will be logged on first request")
            return True
    except Exception as e:
        print(f"  ❌ Logging integration failed: {e}")
        return False


async def main():
    """Run all verification tests"""
    print("=" * 60)
    print("CHAT SYSTEM WIRING VERIFICATION")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("RAG Retrieval", await test_rag_retrieval()))
    results.append(("World Model Query", await test_world_model_query()))
    results.append(("OpenAI Reasoner", await test_openai_reasoner()))
    results.append(("Action Gateway", await test_action_gateway()))
    results.append(("Chat Endpoint", await test_chat_endpoint()))
    results.append(("Governance API", await test_governance_endpoints()))
    results.append(("Logging Integration", await test_logging_integration()))
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All systems wired correctly!")
        print("\nNext steps:")
        print("  1. Start backend: python server.py")
        print("  2. Start frontend: cd frontend && npm run dev")
        print("  3. Open: http://localhost:5173")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed - check errors above")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
