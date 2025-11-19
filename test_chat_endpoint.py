"""
Test the updated /api/chat endpoint with OpenAI integration
"""
import asyncio
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

async def test_chat_endpoint():
    """Test /api/chat endpoint"""
    
    # Check if OpenAI key is set
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        print("⚠️  WARNING: OPENAI_API_KEY not set in .env file")
        print("   The endpoint will return an error message")
        print()
    
    base_url = "http://localhost:8000"
    
    # Test messages
    test_messages = [
        "hi grace",
        "Hello, how are you?",
        "What can you help me with?",
    ]
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for message in test_messages:
            print(f"\n{'='*60}")
            print(f"📤 Testing: '{message}'")
            print(f"{'='*60}")
            
            try:
                response = await client.post(
                    f"{base_url}/api/chat",
                    json={"message": message}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    print(f"✅ Status: {response.status_code}")
                    print(f"\n💬 Reply: {data.get('reply', data.get('response', 'N/A'))}")
                    print(f"\n📊 Confidence: {data.get('confidence', 'N/A')}")
                    print(f"🔗 Citations: {data.get('citations', [])}")
                    print(f"⚙️  Actions: {data.get('actions', [])}")
                    print(f"🤖 Model: {data.get('model', 'N/A')}")
                    
                    if data.get('error'):
                        print(f"⚠️  Error: {data['error']}")
                else:
                    print(f"❌ Error: {response.status_code}")
                    print(f"   {response.text}")
                    
            except Exception as e:
                print(f"❌ Exception: {e}")
    
    print(f"\n{'='*60}")
    print("✅ Test complete!")
    print(f"{'='*60}")

if __name__ == "__main__":
    print("🚀 Testing /api/chat endpoint with OpenAI + RAG + World Model")
    print()
    
    # Make sure server is running
    print("⚠️  Make sure the Grace server is running on http://localhost:8000")
    print("   Run: python server.py")
    print()
    
    asyncio.run(test_chat_endpoint())
