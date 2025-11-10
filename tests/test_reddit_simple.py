"""
Simple Reddit API Integration Test
Tests the Reddit fetch functionality directly
"""

import asyncio
import sys
import os

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))


async def test_reddit_fetch():
    """Test Reddit post fetching directly"""
    
    from backend.reddit_learning import RedditLearning
    
    print("=" * 60)
    print("Testing Reddit API Integration")
    print("=" * 60)
    
    # Create instance
    reddit = RedditLearning()
    
    # Start session
    await reddit.start()
    
    print("\nAPI Status:")
    if reddit.use_real_api:
        print("  [OK] Using real Reddit API")
    else:
        print("  [INFO] Using mock data (no credentials)")
    
    print("\n" + "-" * 60)
    print("Test: Fetching posts from r/programming")
    print("-" * 60)
    
    # Fetch posts directly
    posts = await reddit._fetch_subreddit_posts('r/programming', 5)
    
    print(f"\nFetched {len(posts)} posts:")
    print()
    
    for i, post in enumerate(posts[:3], 1):
        print(f"{i}. {post['title']}")
        print(f"   URL: {post['url']}")
        print(f"   Upvotes: {post['upvotes']}, Comments: {post['comments']}")
        if post.get('text'):
            preview = post['text'][:100].replace('\n', ' ')
            print(f"   Text: {preview}...")
        print()
    
    # Stop session
    await reddit.stop()
    
    print("-" * 60)
    print("Summary")
    print("-" * 60)
    
    if reddit.use_real_api:
        print("\n[SUCCESS] Real Reddit API integration working!")
        print(f"Fetched {len(posts)} real posts from Reddit")
    else:
        print("\n[INFO] Mock data used (no credentials found)")
        print("\nTo use real Reddit API:")
        print("1. Go to https://www.reddit.com/prefs/apps")
        print("2. Create a new app (script type)")
        print("3. Set environment variables:")
        print("   set REDDIT_CLIENT_ID=your_client_id")
        print("   set REDDIT_CLIENT_SECRET=your_client_secret")
        print("\nOR add to .env file:")
        print("   REDDIT_CLIENT_ID=your_client_id")
        print("   REDDIT_CLIENT_SECRET=your_client_secret")
    
    print("\n[SUCCESS] Test completed!")
    print("=" * 60)
    
    return reddit.use_real_api, len(posts)


if __name__ == "__main__":
    use_real_api, post_count = asyncio.run(test_reddit_fetch())
    
    # Exit with status
    if post_count > 0:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure
