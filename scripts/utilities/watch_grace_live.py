#!/usr/bin/env python3
"""
Watch Grace Live - Background Process
Real-time view of what Grace is doing
"""

import asyncio
import websockets
import json
from datetime import datetime


async def watch_grace_activity():
    """Connect to Grace's activity stream and display in real-time"""
    
    print("=" * 80)
    print("WATCHING GRACE - LIVE ACTIVITY FEED")
    print("=" * 80)
    print()
    print("Connecting to Grace's activity stream...")
    print("Backend: ws://localhost:8000/api/activity/stream")
    print("Press Ctrl+C to stop watching")
    print()
    print("-" * 80)
    print()
    
    uri = "ws://localhost:8000/api/activity/stream"
    
    try:
        async with websockets.connect(uri, ping_interval=None) as websocket:
            print("✓ Connected to Grace's activity stream!")
            print()
            print("=" * 80)
            print()
            
            while True:
                try:
                    message = await websocket.recv()
                    data = json.loads(message)
                    
                    if data['type'] == 'history':
                        # Initial history
                        print("📜 Recent History:")
                        print()
                        for event in data['events'][-10:]:  # Show last 10
                            display_event(event)
                        print("-" * 80)
                        print()
                    
                    elif data['type'] == 'current':
                        # Current activity
                        event = data['event']
                        print("🔴 CURRENTLY DOING:")
                        display_event(event, highlight=True)
                        print("-" * 80)
                        print()
                    
                    elif data['type'] == 'event':
                        # New event
                        display_event(data['event'], realtime=True)
                
                except websockets.exceptions.ConnectionClosed:
                    print()
                    print("Connection lost. Reconnecting...")
                    await asyncio.sleep(2)
                    break
    
    except KeyboardInterrupt:
        print()
        print()
        print("=" * 80)
        print("Stopped watching Grace")
        print("=" * 80)
    
    except ConnectionRefusedError:
        print()
        print("=" * 80)
        print("ERROR: Cannot connect to Grace backend")
        print("=" * 80)
        print()
        print("Grace backend is not running!")
        print()
        print("To start Grace:")
        print("  1. Run: START_GRACE_AND_WATCH.bat")
        print("  OR")
        print("  2. In another terminal: python serve.py")
        print("     Then run this script again")
        print()
    
    except Exception as e:
        print(f"Error: {e}")
        print()
        print("Make sure Grace backend is running:")
        print("  python serve.py")
        print()
        print("Or use: START_GRACE_AND_WATCH.bat")


def display_event(event: dict, highlight: bool = False, realtime: bool = False):
    """Display an activity event"""
    
    # Parse timestamp
    timestamp = event['timestamp']
    try:
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        time_str = dt.strftime('%H:%M:%S')
    except:
        time_str = timestamp[:8]
    
    # Get icon
    icons = {
        'thinking': '🧠',
        'pc_command': '💻',
        'browsing': '🌐',
        'sandbox_experiment': '🧪',
        'learning': '📚',
        'proposal': '📝',
        'api_call': '🔌',
        'download': '⬇️',
        'code_generation': '⚡'
    }
    icon = icons.get(event['type'], '•')
    
    # Format output
    if highlight:
        print(f"⚡ [{time_str}] {icon} {event['type'].upper()}: {event['description']}")
    elif realtime:
        print(f"▶️  [{time_str}] {icon} {event['description']}")
    else:
        print(f"  [{time_str}] {icon} {event['description']}")
    
    # Show details
    if event.get('details'):
        for key, value in event['details'].items():
            if isinstance(value, str) and len(value) > 100:
                print(f"    {key}: {value[:100]}...")
            else:
                print(f"    {key}: {value}")
    
    if realtime or highlight:
        print()


async def main():
    """Main loop"""
    while True:
        try:
            await watch_grace_activity()
        except KeyboardInterrupt:
            break
        except:
            print("Retrying in 5 seconds...")
            await asyncio.sleep(5)


if __name__ == '__main__':
    asyncio.run(main())
