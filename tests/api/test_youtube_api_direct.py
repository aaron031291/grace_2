"""
Direct test of YouTube Transcript API integration
Tests the _get_video_transcript method directly without governance
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from backend.youtube_learning import YouTubeLearning


async def test_direct_api():
    """Test YouTube transcript API directly"""
    
    print("\n" + "="*60)
    print("Direct YouTube Transcript API Test")
    print("="*60 + "\n")
    
    test_videos = [
        {
            'id': 'dQw4w9WgXcQ',
            'name': 'Rick Astley - Never Gonna Give You Up',
            'expected': 'success'
        },
        {
            'id': 'fJ9rUzIMcZQ',
            'name': 'Python Programming Tutorial',
            'expected': 'success'
        },
        {
            'id': 'invalid123',
            'name': 'Invalid video ID',
            'expected': 'fail'
        }
    ]
    
    youtube = YouTubeLearning()
    
    results = []
    for i, video in enumerate(test_videos, 1):
        print(f"\n{'-'*60}")
        print(f"Test {i}/3: {video['name']}")
        print(f"{'-'*60}")
        print(f"Video ID: {video['id']}")
        print(f"Expected: {video['expected']}")
        print()
        
        try:
            transcript = await youtube._get_video_transcript(video['id'])
            
            if transcript:
                print(f"[SUCCESS] Transcript fetched")
                print(f"  Length: {len(transcript)} characters")
                print(f"  Word count: ~{len(transcript.split())} words")
                
                results.append({
                    'test': video['name'],
                    'status': 'success',
                    'chars': len(transcript),
                    'words': len(transcript.split())
                })
            else:
                print(f"[FAILED] No transcript returned")
                results.append({
                    'test': video['name'],
                    'status': 'failed',
                    'error': 'No transcript'
                })
                
        except Exception as e:
            error_msg = str(e)
            print(f"[EXCEPTION] {error_msg}")
            results.append({
                'test': video['name'],
                'status': 'exception',
                'error': error_msg
            })
    
    print("\n" + "="*60)
    print("Test Results Summary")
    print("="*60 + "\n")
    
    success_count = sum(1 for r in results if r['status'] == 'success')
    total_count = len(results)
    
    for i, result in enumerate(results, 1):
        status = "PASS" if result['status'] == 'success' else "FAIL"
        print(f"{i}. [{status}] {result['test']}")
        print(f"   Status: {result['status']}")
        if result['status'] == 'success':
            print(f"   Characters: {result.get('chars', 0):,}")
            print(f"   Words: {result.get('words', 0):,}")
        elif 'error' in result:
            print(f"   Error: {result['error']}")
        print()
    
    print(f"{'-'*60}")
    print(f"Success Rate: {success_count}/{total_count}")
    print(f"{'-'*60}\n")
    
    if success_count >= 1:
        print("[SUCCESS] Real YouTube API integration is working!")
        print("Successfully fetched real video transcripts.")
        return True
    else:
        print("[FAILED] No transcripts fetched")
        print("Check if youtube-transcript-api is installed correctly.")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_direct_api())
    sys.exit(0 if success else 1)
