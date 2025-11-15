"""
Grace Real-Time Activity Monitor
Visual display of what Grace is doing autonomously
"""

import requests
import time
import os
from datetime import datetime

API_URL = "http://localhost:8001/api/remote-access"

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def display_dashboard():
    """Display live dashboard"""
    try:
        response = requests.get(f"{API_URL}/dashboard/realtime")
        data = response.json()
        
        clear_screen()
        
        print("=" * 80)
        print("GRACE AUTONOMOUS LEARNING - REAL-TIME MONITOR")
        print("=" * 80)
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Status: {data['status'].upper()}")
        print(f"Current Activity: {data['current_activity']}")
        print()
        
        # Learning Progress
        learning = data.get('learning', {})
        print("-" * 80)
        print("LEARNING PROGRESS")
        print("-" * 80)
        print(f"Current Domain: {learning.get('current_domain', 'None')}")
        print(f"Domains Mastered: {learning.get('domains_mastered', 0)}")
        print(f"Domains In Progress: {learning.get('domains_in_progress', 0)}")
        print(f"Projects Completed: {learning.get('total_projects_completed', 0)}")
        print()
        
        # Model Performance
        models = data.get('models', {})
        print("-" * 80)
        print("MODEL PERFORMANCE")
        print("-" * 80)
        print(f"Total Interactions: {models.get('total_interactions', 0)}")
        print(f"Models Tested: {models.get('models_tested', 0)}")
        best = models.get('best_performers', {})
        if best:
            print("\nBest Performers:")
            for task_type, perf in best.items():
                print(f"  {task_type}: {perf['model']} ({perf['success_rate']:.1%})")
        print()
        
        # Research
        research = data.get('research', {})
        print("-" * 80)
        print("RESEARCH ACTIVITY")
        print("-" * 80)
        print(f"JournalClub: {'Connected' if research.get('journalclub_authenticated') else 'Not connected'}")
        print(f"Papers Downloaded: {research.get('papers_downloaded', 0)}")
        print(f"Papers Processed: {research.get('papers_processed', 0)}")
        print()
        
        # Recent Activities
        recent = data.get('recent_activities', [])
        print("-" * 80)
        print("RECENT ACTIVITIES (Last 10)")
        print("-" * 80)
        for activity in recent[:10]:
            timestamp = activity.get('timestamp', 'unknown')[:19]
            action = activity.get('action', 'unknown')
            resource = activity.get('resource', 'unknown')[:30]
            result = activity.get('result', 'unknown')
            print(f"[{timestamp}] {action:25s} | {resource:30s} | {result}")
        print()
        
        # Capabilities
        caps = data.get('capabilities', {})
        print("-" * 80)
        print("CAPABILITIES")
        print("-" * 80)
        print(f"Autonomous Learning: {'ON' if caps.get('autonomous_learning') else 'OFF'}")
        print(f"Research Access: {'ON' if caps.get('research_access') else 'OFF'}")
        print(f"Sandbox Testing: {'ON' if caps.get('sandbox_testing') else 'OFF'}")
        print(f"Self Upgrade: {'ON' if caps.get('self_upgrade') else 'OFF'}")
        print(f"Models Available: {caps.get('model_count', 0)}")
        print(f"Whitelisted Sites: {caps.get('whitelisted_domains', 0)}")
        print()
        
        print("=" * 80)
        print("Press Ctrl+C to stop monitoring")
        print("=" * 80)
        
    except Exception as e:
        print(f"Error: {e}")

def main():
    print("\nStarting Grace Monitor...")
    print("Connecting to Grace at http://localhost:8001")
    print()
    
    try:
        while True:
            display_dashboard()
            time.sleep(5)  # Update every 5 seconds
            
    except KeyboardInterrupt:
        print("\n\nMonitor stopped.")

if __name__ == "__main__":
    main()