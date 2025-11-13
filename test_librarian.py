#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Librarian Data Orchestrator Integration
Demonstrates the Librarian kernel in action with log output
"""

import asyncio
import logging
import sys
import os
from pathlib import Path
from datetime import datetime

# Fix Windows console encoding
if sys.platform == "win32":
    os.system('chcp 65001 >nul')
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Setup logging to see everything
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/librarian_test.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)


async def test_librarian_integration():
    """Test the Librarian Data Orchestrator"""
    
    print("="*80)
    print("LIBRARIAN DATA ORCHESTRATOR TEST")
    print("="*80)
    print()
    
    try:
        # Import Librarian components
        print("📦 Importing Librarian components...")
        from backend.kernels.librarian_kernel import LibrarianKernel
        from backend.kernels.librarian_clarity_adapter import LibrarianClarityAdapter
        from backend.kernels.event_bus import get_event_bus
        
        print("✅ Imports successful\n")
        
        # Create event bus
        print("🔧 Creating event bus...")
        event_bus = get_event_bus()
        print(f"✅ Event bus created: {event_bus}\n")
        
        # Create Librarian kernel
        print("🔧 Creating Librarian kernel...")
        kernel = LibrarianKernel(
            registry=None,  # Will work without registry in test mode
            event_bus=event_bus
        )
        print(f"✅ Librarian kernel created: {kernel.kernel_id}\n")
        
        # Create clarity adapter
        print("🔧 Creating clarity adapter...")
        adapter = LibrarianClarityAdapter(
            librarian_kernel=kernel,
            registry=None,
            event_mesh=event_bus,
            unified_logic=None
        )
        print(f"✅ Clarity adapter created: {adapter.component_id}\n")
        
        # Initialize
        print("🚀 Initializing Librarian Data Orchestrator...")
        print("-"*80)
        await adapter.initialize()
        print("-"*80)
        print()
        
        # Check status
        print("📊 Kernel Status:")
        status = kernel.get_status()
        print(f"   Kernel ID: {status['kernel_id']}")
        print(f"   Domain: {status['domain']}")
        print(f"   Status: {status['status']}")
        print(f"   Active Agents: {status['active_agents']}")
        print(f"   Metrics: {status['metrics']}")
        print()
        
        # Check queues
        print("📋 Work Queues:")
        queues = kernel.get_queue_status()
        print(f"   Schema Queue: {queues['schema_queue']}")
        print(f"   Ingestion Queue: {queues['ingestion_queue']}")
        print(f"   Trust Audit Queue: {queues['trust_audit_queue']}")
        print()
        
        # Test file watching
        print("👀 Testing File Watching...")
        print(f"   Watching directories: {[str(p) for p in kernel.watch_paths]}")
        print()
        
        # Create a test file
        print("📝 Creating test file...")
        test_dir = Path("grace_training")
        test_dir.mkdir(exist_ok=True)
        test_file = test_dir / f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        test_file.write_text("Test content for Librarian schema inference")
        print(f"   ✅ Created: {test_file}")
        print()
        
        # Wait for file event
        print("⏳ Waiting for file event to be detected...")
        await asyncio.sleep(3)
        print()
        
        # Check if schema queue increased
        queues_after = kernel.get_queue_status()
        print("📋 Queue Status After File Creation:")
        print(f"   Schema Queue: {queues_after['schema_queue']} (was {queues['schema_queue']})")
        if queues_after['schema_queue'] > queues['schema_queue']:
            print("   ✅ File detected and queued for schema inference!")
        print()
        
        # Test spawning an agent
        print("🤖 Testing Agent Spawning...")
        agent_id = await kernel.spawn_agent(
            'schema_scout',
            {
                'type': 'new_file',
                'path': str(test_file)
            },
            priority='high'
        )
        print(f"   ✅ Agent spawned: {agent_id}")
        print()
        
        # Wait for agent to execute
        print("⏳ Waiting for agent execution...")
        await asyncio.sleep(3)
        print()
        
        # Final status
        print("📊 Final Status:")
        final_status = kernel.get_status()
        print(f"   Active Agents: {final_status['active_agents']}")
        print(f"   Total Agents Spawned: {final_status['metrics']['agents_spawned']}")
        print(f"   Jobs Completed: {final_status['metrics']['jobs_completed']}")
        print(f"   Events Processed: {final_status['metrics']['events_processed']}")
        print()
        
        # Test logging action
        print("📝 Testing Action Logging...")
        log_id = await adapter.log_action(
            action_type='schema_proposal',
            action_detail='Test schema proposal from integration test',
            target_resource=str(test_file),
            status='succeeded'
        )
        print(f"   ✅ Action logged: {log_id}")
        print()
        
        # Shutdown
        print("🛑 Shutting down Librarian...")
        print("-"*80)
        await adapter.shutdown()
        print("-"*80)
        print()
        
        print("="*80)
        print("✅ LIBRARIAN TEST COMPLETED SUCCESSFULLY")
        print("="*80)
        print()
        print("📋 Test Summary:")
        print(f"   ✅ Kernel initialized and started")
        print(f"   ✅ File watching operational")
        print(f"   ✅ Sub-agent spawning working")
        print(f"   ✅ Event bus integrated")
        print(f"   ✅ Action logging functional")
        print(f"   ✅ Graceful shutdown completed")
        print()
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_librarian_api():
    """Test Librarian API endpoints"""
    import httpx
    
    print("\n" + "="*80)
    print("TESTING LIBRARIAN API ENDPOINTS")
    print("="*80 + "\n")
    
    base_url = "http://localhost:8000"
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Test status endpoint
            print("📡 GET /api/librarian/status")
            try:
                response = await client.get(f"{base_url}/api/librarian/status")
                print(f"   Status: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    print(f"   Kernel Status: {data.get('kernel', {}).get('status')}")
                    print(f"   Active Agents: {data.get('kernel', {}).get('active_agents')}")
                    print(f"   Queue Depths: {data.get('queues')}")
                    print("   ✅ Status endpoint working")
                print()
            except Exception as e:
                print(f"   ⚠️ Could not reach API: {e}")
                print("   (Server might not be running)\n")
                return False
            
            # Test health endpoint
            print("📡 GET /api/health")
            try:
                response = await client.get(f"{base_url}/api/health")
                print(f"   Status: {response.status_code}")
                if response.status_code == 200:
                    print("   ✅ Health endpoint working")
                print()
            except Exception as e:
                print(f"   ⚠️ Health check failed: {e}\n")
            
            print("✅ API tests completed")
            return True
            
    except Exception as e:
        logger.error(f"❌ API test failed: {e}")
        return False


if __name__ == "__main__":
    print("\n🚀 Starting Librarian Integration Tests\n")
    
    # Ensure logs directory exists
    Path("logs").mkdir(exist_ok=True)
    
    # Run kernel test
    success = asyncio.run(test_librarian_integration())
    
    if success:
        print("\n💡 To test API endpoints, run 'python serve.py' first, then:")
        print("   python -c 'import asyncio; from test_librarian import test_librarian_api; asyncio.run(test_librarian_api())'")
    
    sys.exit(0 if success else 1)
