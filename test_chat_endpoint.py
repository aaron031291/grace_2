"""
Quick test script for /api/chat endpoint

Tests:
1. Simple chat message
2. Chat with approval required
3. Session continuity
"""

import asyncio
import httpx


async def test_simple_chat():
    """Test basic chat response"""
    print("\n[TEST 1] Simple chat message...")
    
    async with httpx.AsyncClient(base_url="http://localhost:8420") as client:
        response = await client.post(
            "/api/chat",
            json={
                "message": "Hello Grace, what's your current status?",
                "user_id": "test_user"
            },
            timeout=30.0
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Status: {response.status_code}")
            print(f"✓ Reply: {data['reply'][:100]}...")
            print(f"✓ Confidence: {data['confidence']}")
            print(f"✓ Session ID: {data['session_id']}")
            print(f"✓ Citations: {data['citations']}")
            return data['session_id']
        else:
            print(f"✗ Failed: {response.status_code}")
            print(f"  Error: {response.text}")
            return None


async def test_session_continuity(session_id: str):
    """Test conversation history works"""
    print(f"\n[TEST 2] Session continuity with session_id={session_id}...")
    
    async with httpx.AsyncClient(base_url="http://localhost:8420") as client:
        response = await client.post(
            "/api/chat",
            json={
                "message": "What did I just ask you?",
                "session_id": session_id,
                "user_id": "test_user"
            },
            timeout=30.0
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Status: {response.status_code}")
            print(f"✓ Reply: {data['reply'][:150]}...")
            print(f"✓ Confidence: {data['confidence']}")
        else:
            print(f"✗ Failed: {response.status_code}")


async def test_action_approval():
    """Test action requiring approval"""
    print("\n[TEST 3] Action requiring approval...")
    
    async with httpx.AsyncClient(base_url="http://localhost:8420") as client:
        response = await client.post(
            "/api/chat",
            json={
                "message": "Create a new database table called 'test_users' with id and name fields",
                "user_id": "test_user"
            },
            timeout=30.0
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Status: {response.status_code}")
            print(f"✓ Reply: {data['reply'][:150]}...")
            print(f"✓ Requires Approval: {data['requires_approval']}")
            print(f"✓ Actions Proposed: {len(data['actions'])}")
            if data['actions']:
                print(f"  Action: {data['actions'][0]}")
        else:
            print(f"✗ Failed: {response.status_code}")


async def test_chat_history(session_id: str):
    """Test chat history retrieval"""
    print(f"\n[TEST 4] Chat history for session {session_id}...")
    
    async with httpx.AsyncClient(base_url="http://localhost:8420") as client:
        response = await client.get(
            f"/api/chat/history/{session_id}",
            timeout=10.0
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Status: {response.status_code}")
            print(f"✓ Total messages: {data['total_messages']}")
            print(f"✓ Messages returned: {len(data['messages'])}")
        else:
            print(f"✗ Failed: {response.status_code}")


async def main():
    """Run all tests"""
    print("=" * 60)
    print("Testing /api/chat endpoint")
    print("=" * 60)
    
    try:
        # Test 1: Simple chat
        session_id = await test_simple_chat()
        
        if session_id:
            # Test 2: Session continuity
            await test_session_continuity(session_id)
            
            # Test 4: Chat history
            await test_chat_history(session_id)
        
        # Test 3: Action approval (separate session)
        await test_action_approval()
        
        print("\n" + "=" * 60)
        print("All tests complete!")
        print("=" * 60)
    
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("\n[INFO] Make sure the backend is running on http://localhost:8420")
    print("[INFO] Start it with: python backend/main.py\n")
    
    asyncio.run(main())
