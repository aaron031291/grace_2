"""
Test YouTube Real API Integration
Tests that youtube_learning.py can fetch real YouTube transcripts
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from backend.youtube_learning import youtube_learning


async def test_real_youtube_video():
    """Test fetching a real YouTube video transcript"""
    
    print("\n" + "="*60)
    print("Testing Real YouTube API Integration")
    print("="*60 + "\n")
    
    test_videos = [
        {
            'url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
            'name': 'Popular music video (Rick Astley - Never Gonna Give You Up)',
            'topic': 'music'
        },
        {
            'url': 'https://www.youtube.com/watch?v=fJ9rUzIMcZQ',
            'name': 'Python Programming Tutorial',
            'topic': 'programming'
        },
        {
            'url': 'https://www.youtube.com/watch?v=invalid123',
            'name': 'Invalid video (should fail gracefully)',
            'topic': 'test'
        }
    ]
    
    await youtube_learning.start()
    
    results = []
    for i, video_data in enumerate(test_videos, 1):
        print(f"\n{'-'*60}")
        print(f"Test {i}/3: {video_data['name']}")
        print(f"{'-'*60}")
        print(f"URL: {video_data['url']}")
        print(f"Topic: {video_data['topic']}")
        print()
        
        try:
            result = await youtube_learning.learn_from_video(
                video_url=video_data['url'],
                topic=video_data['topic']
            )
            
            if 'error' in result:
                print(f"FAILED: {result['error']}")
                results.append({
                    'test': video_data['name'],
                    'status': 'failed',
                    'error': result['error']
                })
            else:
                print(f"SUCCESS!")
                print(f"  Video ID: {result.get('video_id')}")
                print(f"  Source ID: {result.get('source_id')}")
                print(f"  Title: {result.get('title')}")
                print(f"  Channel: {result.get('channel')}")
                print(f"  Word Count: {result.get('word_count')}")
                print(f"  Traceable: {result.get('fully_traceable')}")
                
                results.append({
                    'test': video_data['name'],
                    'status': 'success',
                    'word_count': result.get('word_count', 0),
                    'source_id': result.get('source_id')
                })
        except Exception as e:
            print(f"EXCEPTION: {str(e)}")
            results.append({
                'test': video_data['name'],
                'status': 'exception',
                'error': str(e)
            })
        
        await asyncio.sleep(1)
    
    await youtube_learning.stop()
    
    print("\n" + "="*60)
    print("Test Results Summary")
    print("="*60 + "\n")
    
    success_count = sum(1 for r in results if r['status'] == 'success')
    total_count = len(results)
    
    for i, result in enumerate(results, 1):
        status_icon = "PASS" if result['status'] == 'success' else "FAIL"
        print(f"{i}. [{status_icon}] {result['test']}")
        print(f"   Status: {result['status']}")
        if result['status'] == 'success':
            print(f"   Words: {result.get('word_count', 0)}")
        elif 'error' in result:
            print(f"   Error: {result['error']}")
        print()
    
    print(f"{'-'*60}")
    print(f"Success Rate: {success_count}/{total_count} ({success_count*100//total_count if total_count > 0 else 0}%)")
    print(f"{'-'*60}\n")
    
    if success_count >= 1:
        print("REAL YOUTUBE API INTEGRATION WORKING!")
        print("At least one video transcript was successfully fetched.")
    else:
        print("NO VIDEOS SUCCESSFULLY FETCHED")
        print("Check error logs above for details.")
    
    return success_count >= 1


if __name__ == "__main__":
    success = asyncio.run(test_real_youtube_video())
    sys.exit(0 if success else 1)
