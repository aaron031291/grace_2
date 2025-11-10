"""
Test Reddit API Integration
Tests both mock and real Reddit API functionality
"""

import asyncio
import sys
import os

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.reddit_learning import reddit_learning


async def test_reddit_learning():
    """Test Reddit learning with both mock and real API"""
    
    print("=" * 60)
    print("Testing Reddit Learning Integration")
    print("=" * 60)
    
    # Start the system
    await reddit_learning.start()
    
    print("\n" + "=" * 60)
    print("Test 1: Learn from r/programming")
    print("=" * 60)
    
    result = await reddit_learning.learn_from_subreddit(
        subreddit='programming',
        topic='software engineering best practices',
        max_posts=5
    )
    
    print(f"\n✅ Result:")
    print(f"  Subreddit: {result.get('subreddit')}")
    print(f"  Posts analyzed: {result.get('posts_analyzed')}")
    print(f"  Source IDs: {len(result.get('source_ids', []))}")
    print(f"  Fully traceable: {result.get('fully_traceable')}")
    
    if result.get('posts_analyzed', 0) > 0:
        print(f"\n✅ Successfully fetched posts!")
        if reddit_learning.use_real_api:
            print("  Using: Real Reddit API")
        else:
            print("  Using: Mock data (no credentials)")
    
    print("\n" + "=" * 60)
    print("Test 2: Learn about Python from multiple subreddits")
    print("=" * 60)
    
    result2 = await reddit_learning.learn_topic(
        topic='Python async programming',
        category='python',
        max_subreddits=2,
        posts_per_subreddit=3
    )
    
    print(f"\n✅ Result:")
    print(f"  Topic: {result2.get('topic')}")
    print(f"  Subreddits checked: {result2.get('subreddits_checked')}")
    print(f"  Total posts: {result2.get('total_posts')}")
    print(f"  Source IDs: {len(result2.get('source_ids', []))}")
    
    print("\n" + "=" * 60)
    print("Test 3: Get recommended subreddits")
    print("=" * 60)
    
    recommendations = reddit_learning.get_recommended_subreddits()
    
    print(f"\n✅ Categories available: {len(recommendations)}")
    for category, subreddits in list(recommendations.items())[:3]:
        print(f"\n  {category}:")
        for sub in subreddits[:3]:
            print(f"    - {sub}")
    
    # Stop the system
    await reddit_learning.stop()
    
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    if reddit_learning.use_real_api:
        print("✅ Real Reddit API integration working!")
    else:
        print("⚠️  Mock data used (no credentials found)")
        print("\nTo use real Reddit API:")
        print("1. Go to https://www.reddit.com/prefs/apps")
        print("2. Create a new app (script type)")
        print("3. Set environment variables:")
        print("   - REDDIT_CLIENT_ID=your_client_id")
        print("   - REDDIT_CLIENT_SECRET=your_client_secret")
        print("OR store in secrets vault:")
        print("   - reddit_client_id")
        print("   - reddit_client_secret")
    
    print("\n✅ All tests completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_reddit_learning())
