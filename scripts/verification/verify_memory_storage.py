"""Verify that host registrations are being stored as JSON"""

import asyncio
import sys
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.models.models import ChatMessage
from backend.models.base_models import async_session
from sqlalchemy import select, desc


async def verify_storage():
    print("Checking memory storage...")
    
    async with async_session() as session:
        # Get recent infrastructure manager messages
        result = await session.execute(
            select(ChatMessage)
            .where(ChatMessage.user == 'infrastructure_manager')
            .order_by(desc(ChatMessage.created_at))
            .limit(3)
        )
        messages = result.scalars().all()
        
        print(f"\nFound {len(messages)} infrastructure messages:\n")
        
        for i, msg in enumerate(messages, 1):
            print(f"Message {i}:")
            print(f"  Role: {msg.role}")
            print(f"  Created: {msg.created_at}")
            print(f"  Content length: {len(msg.content)} chars")
            
            # Try to parse as JSON
            try:
                data = json.loads(msg.content)
                print(f"  [OK] Valid JSON!")
                print(f"  Type: {data.get('type', data.get('host_id', 'unknown'))}")
                if 'host_id' in data:
                    print(f"  Host ID: {data['host_id']}")
                    print(f"  OS Type: {data.get('os_type', 'unknown')}")
                if 'timestamp' in data:
                    print(f"  Timestamp: {data['timestamp']}")
                print(f"  Sample: {json.dumps(data, indent=2)[:200]}...")
            except json.JSONDecodeError:
                print(f"  [WARN] Not valid JSON")
                print(f"  Content: {msg.content[:100]}...")
            
            print()
        
        if messages and all(msg.content.startswith('{') for msg in messages):
            print("[SUCCESS] All messages are properly stored as JSON blobs!")
        else:
            print("[PARTIAL] Some messages may not be JSON formatted")


if __name__ == "__main__":
    asyncio.run(verify_storage())
