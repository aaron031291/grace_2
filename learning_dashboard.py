"""
Grace Learning Dashboard
Real-time visibility into Grace's data absorption and learning activities
"""

import requests
import time
import os
from datetime import datetime
from typing import Dict, Any

API_URL = "http://localhost:8001/api/learning"

class LearningDashboard:
    """Interactive dashboard for monitoring Grace's learning"""
    
    def __init__(self):
        self.api_url = API_URL
        self.last_activity_count = 0
        self.refresh_rate = 3  # seconds
    
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def format_bytes(self, bytes_val: int) -> str:
        """Format bytes to human-readable string"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_val < 1024.0:
                return f"{bytes_val:.2f} {unit}"
            bytes_val /= 1024.0
        return f"{bytes_val:.2f} TB"
    
    def get_status_emoji(self, status: str) -> str:
        """Get emoji for status"""
        status_map = {
            'initiated': '🔵',
            'in_progress': '🟡',
            'processing': '⚙️',
            'absorbed': '✅',
            'validated': '✅',
            'failed': '❌',
            'rejected': '⛔'
        }
        return status_map.get(status.lower(), '❓')
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Fetch dashboard data from API"""
        try:
            response = requests.get(f"{self.api_url}/dashboard/realtime", timeout=5)
            if response.status_code == 200:
                return response.json().get('data', {})
            else:
                return {"error": f"API returned {response.status_code}"}
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
    
    def get_analytics(self) -> Dict[str, Any]:
        """Fetch analytics data"""
        try:
            response = requests.get(f"{self.api_url}/analytics", timeout=5)
            if response.status_code == 200:
                return response.json().get('data', {})
            return {}
        except:
            return {}
    
    def display_header(self):
        """Display dashboard header"""
        print("=" * 100)
        print(" " * 30 + "🧠 GRACE LEARNING DASHBOARD 🧠")
        print("=" * 100)
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Refresh Rate: {self.refresh_rate}s")
        print("=" * 100)
        print()
    
    def display_active_session(self, session: Dict[str, Any]):
        """Display active learning session info"""
        if not session:
            print("📊 ACTIVE SESSION: None")
            print()
            return
        
        print("📊 ACTIVE SESSION")
        print("-" * 100)
        print(f"Session ID: {session.get('session_id', 'N/A')}")
        print(f"Target Domain: {session.get('target_domain', 'N/A')}")
        print(f"Started: {session.get('started_at', 'N/A')[:19]}")
        print(f"Activities: {len(session.get('activities', []))}")
        print(f"Data Absorbed: {self.format_bytes(session.get('total_data_absorbed', 0))}")
        print(f"Validation Score: {session.get('validation_score', 0):.1%}")
        print(f"Status: {session.get('status', 'unknown').upper()}")
        
        goals = session.get('goals', [])
        if goals:
            print(f"Goals: {', '.join(goals[:3])}")
        
        achievements = session.get('achievements', [])
        if achievements:
            print(f"Achievements: {', '.join(achievements[:2])}")
        print()
    
    def display_metrics(self, data: Dict[str, Any]):
        """Display key metrics"""
        print("📈 KEY METRICS")
        print("-" * 100)
        
        col1_width = 50
        col2_width = 50
        
        # Left column
        print(f"Total Activities: {data.get('total_activities', 0):,}".ljust(col1_width), end="")
        print(f"Validated: {data.get('validated_activities', 0):,}")
        
        validation_rate = data.get('validation_rate', 0)
        health = data.get('health', {}).get('validation_health', 'unknown')
        health_emoji = {'good': '🟢', 'warning': '🟡', 'poor': '🔴'}.get(health, '⚪')
        
        print(f"Validation Rate: {validation_rate:.1%} {health_emoji}".ljust(col1_width), end="")
        print(f"Data Absorbed: {self.format_bytes(data.get('total_data_absorbed_bytes', 0))}")
        
        print(f"Sessions: {data.get('sessions_count', 0)}".ljust(col1_width), end="")
        print(f"Total Size (MB): {data.get('total_data_absorbed_mb', 0):.2f}")
        print()
    
    def display_learning_rate(self, rates: Dict[str, float]):
        """Display learning velocity"""
        print("⚡ LEARNING VELOCITY")
        print("-" * 100)
        print(f"Last 5 min: {rates.get('last_5_min', 0)} activities | ", end="")
        print(f"Last 15 min: {rates.get('last_15_min', 0)} | ", end="")
        print(f"Last Hour: {rates.get('last_hour', 0)} | ", end="")
        print(f"Last 24h: {rates.get('last_24h', 0)}")
        print()
    
    def display_source_breakdown(self, sources: Dict[str, int]):
        """Display learning sources breakdown"""
        if not sources:
            return
        
        print("📚 LEARNING SOURCES")
        print("-" * 100)
        
        # Sort by count descending
        sorted_sources = sorted(sources.items(), key=lambda x: x[1], reverse=True)
        
        for source, count in sorted_sources[:8]:
            source_name = source.replace('_', ' ').title()
            bar_length = min(int(count / max(sources.values()) * 40), 40)
            bar = '█' * bar_length
            print(f"{source_name:25s} {bar:40s} {count:4d}")
        print()
    
    def display_recent_activities(self, activities: list):
        """Display recent learning activities"""
        if not activities:
            print("📋 RECENT ACTIVITIES: None yet")
            print()
            return
        
        print("📋 RECENT ACTIVITIES (Last 15)")
        print("-" * 100)
        print(f"{'Time':<12} {'Status':<12} {'Source':<20} {'URL':<35} {'Size':<10} {'Score':<8}")
        print("-" * 100)
        
        for activity in activities[:15]:
            timestamp = activity.get('timestamp', '')[:19].split('T')
            time_str = timestamp[1] if len(timestamp) > 1 else timestamp[0]
            
            status = activity.get('status', 'unknown')
            status_emoji = self.get_status_emoji(status)
            status_display = f"{status_emoji} {status[:9]}"
            
            source = activity.get('source_type', 'unknown').replace('_', ' ')[:18]
            url = activity.get('source_url', 'N/A')[:33]
            size = f"{activity.get('size_kb', 0):.1f} KB"
            score = activity.get('validation_score', 0)
            score_display = f"{score:.1%}" if score > 0 else "-"
            
            print(f"{time_str:<12} {status_display:<12} {source:<20} {url:<35} {size:<10} {score_display:<8}")
        print()
    
    def display_alerts(self, alerts: list):
        """Display system alerts"""
        if not alerts:
            return
        
        print("⚠️  ALERTS")
        print("-" * 100)
        for alert in alerts:
            severity = alert.get('severity', 'info')
            emoji = {'error': '🔴', 'warning': '🟡', 'info': '🔵'}.get(severity, '⚪')
            message = alert.get('message', 'Unknown alert')
            print(f"{emoji} {message}")
        print()
    
    def display_analytics_summary(self, analytics: Dict[str, Any]):
        """Display analytics summary"""
        if not analytics or 'message' in analytics:
            return
        
        print("📊 ANALYTICS SUMMARY")
        print("-" * 100)
        
        activities = analytics.get('activities', {})
        data_volume = analytics.get('data_volume', {})
        velocity = analytics.get('learning_velocity', {})
        
        print(f"Success Rate: {activities.get('success_rate', 0):.1%} | ", end="")
        print(f"Failed: {activities.get('failed', 0)} | ", end="")
        print(f"In Progress: {activities.get('in_progress', 0)}")
        
        print(f"Total Data: {data_volume.get('total_mb', 0):.2f} MB ({data_volume.get('total_gb', 0):.3f} GB)")
        print(f"Avg per Activity: {data_volume.get('avg_per_activity_kb', 0):.2f} KB")
        
        print(f"Learning Velocity: {velocity.get('activities_per_hour', 0):.1f} activities/hour | ", end="")
        print(f"{velocity.get('mb_per_hour', 0):.2f} MB/hour")
        print()
    
    def display_help(self):
        """Display help information"""
        print("🔧 CONTROLS")
        print("-" * 100)
        print("Press Ctrl+C to stop monitoring")
        print("View detailed analytics at: http://localhost:8001/api/learning/analytics")
        print("View API docs at: http://localhost:8001/docs")
        print("=" * 100)
    
    def display(self):
        """Display complete dashboard"""
        data = self.get_dashboard_data()
        
        if 'error' in data:
            self.clear_screen()
            print("=" * 100)
            print(" " * 35 + "❌ CONNECTION ERROR")
            print("=" * 100)
            print(f"\nError: {data['error']}")
            print("\nMake sure Grace backend is running: python serve.py")
            print("API endpoint: " + self.api_url)
            print("\nRetrying in 5 seconds...")
            time.sleep(5)
            return
        
        self.clear_screen()
        self.display_header()
        self.display_active_session(data.get('active_session'))
        self.display_metrics(data)
        self.display_learning_rate(data.get('current_learning_rate', {}))
        self.display_source_breakdown(data.get('source_breakdown', {}))
        self.display_recent_activities(data.get('recent_activities', []))
        self.display_alerts(data.get('alerts', []))
        
        # Fetch and display analytics periodically
        if time.time() % 30 < self.refresh_rate:  # Every 30 seconds
            analytics = self.get_analytics()
            self.display_analytics_summary(analytics)
        
        self.display_help()
        
        # Check for new activities
        current_count = data.get('total_activities', 0)
        if current_count > self.last_activity_count:
            print(f"\n🆕 {current_count - self.last_activity_count} new activities detected!")
            self.last_activity_count = current_count
    
    def run(self):
        """Run the dashboard"""
        print("\n🚀 Starting Grace Learning Dashboard...")
        print(f"Connecting to: {self.api_url}")
        print("Please wait...\n")
        
        time.sleep(2)
        
        try:
            while True:
                self.display()
                time.sleep(self.refresh_rate)
        except KeyboardInterrupt:
            self.clear_screen()
            print("\n" + "=" * 100)
            print(" " * 35 + "👋 Dashboard Stopped")
            print("=" * 100)
            print("\nThank you for monitoring Grace's learning activities!")
            print()


def main():
    """Main entry point"""
    dashboard = LearningDashboard()
    dashboard.run()


if __name__ == "__main__":
    main()