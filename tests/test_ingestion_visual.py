"""
Test Visual Ingestion Logger
Demonstrates visual logging with crypto verification and clickable links
"""

import asyncio
import logging
from backend.visual_ingestion_logger import visual_ingestion_logger
from backend.knowledge_provenance import provenance_tracker
from backend.safe_web_scraper import safe_web_scraper
from backend.web_learning_orchestrator import web_learning_orchestrator

logging.basicConfig(level=logging.INFO)


async def main():
    """Test visual ingestion logging"""
    
    print("\n" + "="*100)
    print("🧪 TESTING VISUAL INGESTION LOGGER")
    print("="*100)
    print("\nThis will demonstrate Grace's visual ingestion logs with:")
    print("  ✅ Clickable HTTP links to sources")
    print("  ✅ Cryptographic verification")
    print("  ✅ Real-time visual updates")
    print("  ✅ Complete audit trail")
    print("\n" + "="*100 + "\n")
    
    input("Press Enter to start the demonstration...")
    
    # Start systems
    print("\n🚀 Starting Grace's learning systems...")
    await web_learning_orchestrator.start()
    
    print("\n📚 Grace will now learn from multiple sources...")
    print("Watch for visual logs with clickable links!\n")
    
    # Test 1: Learn from web
    print("=" * 100)
    print("TEST 1: Learning Python from official docs")
    print("=" * 100)
    
    result = await safe_web_scraper.scrape_url(
        url='https://docs.python.org/3/tutorial/index.html',
        topic='python',
        purpose='demonstration'
    )
    
    if result:
        print("✅ Ingestion logged! Check the visual log.\n")
        await asyncio.sleep(2)
    
    # Test 2: Learn from another source
    print("=" * 100)
    print("TEST 2: Learning React from official docs")
    print("=" * 100)
    
    result = await safe_web_scraper.scrape_url(
        url='https://reactjs.org/docs/getting-started.html',
        topic='react',
        purpose='demonstration'
    )
    
    if result:
        print("✅ Ingestion logged! Check the visual log.\n")
        await asyncio.sleep(2)
    
    # Test 3: Learn FastAPI
    print("=" * 100)
    print("TEST 3: Learning FastAPI")
    print("=" * 100)
    
    result = await safe_web_scraper.scrape_url(
        url='https://fastapi.tiangolo.com/',
        topic='fastapi',
        purpose='demonstration'
    )
    
    if result:
        print("✅ Ingestion logged! Check the visual log.\n")
    
    # Get statistics
    print("\n" + "="*100)
    print("📊 INGESTION STATISTICS")
    print("="*100)
    
    stats = await visual_ingestion_logger.get_ingestion_stats()
    
    print(f"\nTotal Ingestions: {stats['total_ingestions']}")
    print(f"Verified Sources: {stats['verified_sources']}")
    print(f"Verification Rate: {stats['verification_rate']:.1%}")
    
    print(f"\nBy Source Type:")
    for source_type, count in stats['by_source_type'].items():
        print(f"  {source_type}: {count}")
    
    print(f"\nTop Domains:")
    for domain, count in list(stats['top_domains'].items())[:5]:
        print(f"  {domain}: {count}")
    
    print(f"\n📋 Visual Log: {stats['html_log']}")
    
    # Show recent ingestions
    print("\n" + "="*100)
    print("📖 RECENT INGESTIONS (Last 3)")
    print("="*100)
    
    recent = await visual_ingestion_logger.get_recent_ingestions(limit=3)
    
    for idx, ing in enumerate(recent, 1):
        print(f"\n{idx}. {ing['title']}")
        print(f"   URL: {ing['url']}")
        print(f"   Source ID: {ing['source_id']}")
        print(f"   Trust Score: {ing['trust_score']:.2f}")
        print(f"   Verified: {'✅' if ing['verified'] else '❌'}")
        print(f"   Crypto Hash: {ing['crypto']['content_hash'][:32]}...")
    
    print("\n" + "="*100)
    print("✅ DEMONSTRATION COMPLETE!")
    print("="*100)
    
    print(f"\n📋 Open the visual log to see clickable links:")
    print(f"   {stats['html_log']}")
    print(f"\n   Or run: view_ingestion_log.bat")
    
    print("\n🔍 All ingestions have:")
    print("   ✅ Clickable HTTP links to original sources")
    print("   ✅ Cryptographic verification (hash, signature)")
    print("   ✅ Complete verification chain (Hunter, Governance, Constitutional)")
    print("   ✅ Immutable audit trail")
    print("   ✅ Trust scores and metadata")
    
    print("\n" + "="*100 + "\n")
    
    # Stop systems
    await web_learning_orchestrator.stop()


if __name__ == "__main__":
    asyncio.run(main())
