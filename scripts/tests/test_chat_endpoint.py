"""
Quick test script for /api/chat endpoint

Tests:
1. Simple chat message
2. Chat with approval required
3. Session continuity
"""

import os
import asyncio
import httpx
import sys

# Configuration
DEFAULT_PORT = 8000
try:
    PORT = int(os.getenv("GRACE_PORT", str(DEFAULT_PORT)))
except ValueError:
    PORT = DEFAULT_PORT

BASE_URL = f"http://localhost:{PORT}"

# Unicode safe symbols for Windows consoles
if sys.platform == 'win32':
    CHECK_MARK = "[OK]"
    CROSS_MARK = "[FAIL]"
else:
    CHECK_MARK = "✓"
    CROSS_MARK = "✗"

async def test_simple_chat():
    """Test basic chat response"""
    print("\n[TEST 1] Simple chat message...")
    
    try:
        async with httpx.AsyncClient(base_url=BASE_URL) as client:
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
                print(f"{CHECK_MARK} Status: {response.status_code}")
                print(f"{CHECK_MARK} Reply: {data.get('reply', '')[:100]}...")
                print(f"{CHECK_MARK} Confidence: {data.get('confidence', 'N/A')}")
                print(f"{CHECK_MARK} Session ID: {data.get('session_id', 'N/A')}")
                print(f"{CHECK_MARK} Citations: {data.get('citations', [])}")
                return data.get('session_id')
            else:
                print(f"{CROSS_MARK} Failed: {response.status_code}")
                print(f"  Error: {response.text}")
                return None
    except httpx.ConnectError:
        print(f"{CROSS_MARK} Connection failed. Is the server running on {BASE_URL}?")
        return None

async def test_session_continuity(session_id: str):
    """Test conversation history works"""
    print(f"\n[TEST 2] Session continuity with session_id={session_id}...")
    
    try:
        async with httpx.AsyncClient(base_url=BASE_URL) as client:
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
                print(f"{CHECK_MARK} Status: {response.status_code}")
                print(f"{CHECK_MARK} Reply: {data.get('reply', '')[:150]}...")
                print(f"{CHECK_MARK} Confidence: {data.get('confidence', 'N/A')}")
            else:
                print(f"{CROSS_MARK} Failed: {response.status_code}")
    except Exception as e:
        print(f"{CROSS_MARK} Error: {e}")

async def test_action_approval():
    """Test action requiring approval"""
    print("\n[TEST 3] Action requiring approval...")
    
    try:
        async with httpx.AsyncClient(base_url=BASE_URL) as client:
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
                print(f"{CHECK_MARK} Status: {response.status_code}")
                print(f"{CHECK_MARK} Reply: {data.get('reply', '')[:150]}...")
                print(f"{CHECK_MARK} Requires Approval: {data.get('requires_approval', False)}")
                actions = data.get('actions', [])
                print(f"{CHECK_MARK} Actions Proposed: {len(actions)}")
                if actions:
                    print(f"  Action: {actions[0]}")
            else:
                print(f"{CROSS_MARK} Failed: {response.status_code}")
    except Exception as e:
        print(f"{CROSS_MARK} Error: {e}")

async def test_chat_history(session_id: str):
    """Test chat history retrieval"""
    print(f"\n[TEST 4] Chat history for session {session_id}...")
    
    try:
        async with httpx.AsyncClient(base_url=BASE_URL) as client:
            response = await client.get(
                f"/api/chat/history/{session_id}",
                timeout=10.0
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"{CHECK_MARK} Status: {response.status_code}")
                print(f"{CHECK_MARK} Total messages: {data.get('total_messages', 0)}")
                print(f"{CHECK_MARK} Messages returned: {len(data.get('messages', []))}")
            else:
                print(f"{CROSS_MARK} Failed: {response.status_code}")
    except Exception as e:
        print(f"{CROSS_MARK} Error: {e}")

async def main():
    """Run all tests"""
    print("=" * 60)
    print(f"Testing /api/chat endpoint on {BASE_URL}")
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
        print(f"\n{CROSS_MARK} Test failed with error: {e}")
        # Only print traceback if it's not a connection error (handled above)
        if not isinstance(e, httpx.ConnectError):
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    print(f"\n[INFO] Make sure the backend is running on {BASE_URL}")
    print("[INFO] Start it with: python server.py\n")
    
    asyncio.run(main())

