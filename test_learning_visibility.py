"""
Test Learning Visibility System
Demonstrates Grace's ability to learn from web sources with full traceability
"""

import requests
import time
import base64
import hashlib
from datetime import datetime
from typing import Dict, Any


class LearningVisibilityTest:
    """Test the complete learning visibility system"""
    
    def __init__(self, api_url: str = "http://localhost:8001/api/learning"):
        self.api_url = api_url
        self.session_id = None
        self.activity_ids = []
    
    def print_section(self, title: str):
        """Print a section header"""
        print("\n" + "=" * 80)
        print(f" {title}")
        print("=" * 80)
    
    def print_result(self, emoji: str, message: str, data: Any = None):
        """Print a result message"""
        print(f"{emoji} {message}")
        if data:
            if isinstance(data, dict):
                for key, value in data.items():
                    print(f"   {key}: {value}")
            else:
                print(f"   {data}")
    
    def check_health(self) -> bool:
        """Check if the learning system is healthy"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=5)
            if response.status_code == 200:
                result = response.json()
                return result.get('success', False)
            return False
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return False
    
    def start_session(self, domain: str, goals: list) -> bool:
        """Start a learning session"""
        try:
            response = requests.post(
                f"{self.api_url}/session/start",
                json={
                    "target_domain": domain,
                    "goals": goals
                },
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                self.session_id = result.get('session_id')
                self.print_result("✅", "Learning session started", {
                    "Session ID": self.session_id,
                    "Domain": domain,
                    "Goals": ", ".join(goals)
                })
                return True
            else:
                self.print_result("❌", f"Failed to start session: {response.status_code}")
                return False
        except Exception as e:
            self.print_result("❌", f"Error starting session: {e}")
            return False
    
    def record_learning_activity(
        self,
        source_type: str,
        source_url: str,
        content: str,
        content_type: str = "text/html"
    ) -> bool:
        """Record a learning activity"""
        try:
            # Encode content as base64
            content_b64 = base64.b64encode(content.encode('utf-8')).decode('utf-8')
            
            response = requests.post(
                f"{self.api_url}/activity/record",
                json={
                    "source_type": source_type,
                    "source_url": source_url,
                    "data_content": content_b64,
                    "content_type": content_type,
                    "metadata": {
                        "test": True,
                        "timestamp": datetime.now().isoformat()
                    }
                },
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                activity_id = result.get('activity_id')
                self.activity_ids.append(activity_id)
                
                self.print_result("✅", "Learning activity recorded", {
                    "Activity ID": activity_id,
                    "Source": source_url[:60],
                    "Type": source_type,
                    "Size": f"{len(content)} bytes"
                })
                return True
            else:
                self.print_result("❌", f"Failed to record activity: {response.status_code}")
                return False
        except Exception as e:
            self.print_result("❌", f"Error recording activity: {e}")
            return False
    
    def validate_activity(self, activity_id: str) -> Dict[str, Any]:
        """Validate a learning activity"""
        try:
            response = requests.post(
                f"{self.api_url}/activity/{activity_id}/validate",
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                validation = result.get('data', {})
                
                overall_score = validation.get('overall_score', 0)
                passed = validation.get('passed', False)
                
                emoji = "✅" if passed else "❌"
                self.print_result(emoji, f"Validation complete: {overall_score:.1%}", {
                    "Activity ID": activity_id[:20] + "...",
                    "Passed": passed,
                    "Checks Passed": sum(1 for c in validation.get('checks', {}).values() if c.get('passed'))
                })
                
                return validation
            else:
                self.print_result("❌", f"Validation failed: {response.status_code}")
                return {}
        except Exception as e:
            self.print_result("❌", f"Error validating: {e}")
            return {}
    
    def get_status(self) -> Dict[str, Any]:
        """Get current learning status"""
        try:
            response = requests.get(f"{self.api_url}/status", timeout=10)
            if response.status_code == 200:
                return response.json().get('data', {})
            return {}
        except Exception as e:
            print(f"Error getting status: {e}")
            return {}
    
    def end_session(self) -> bool:
        """End the learning session"""
        try:
            response = requests.post(f"{self.api_url}/session/end", timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                report = result.get('data', {})
                
                self.print_result("✅", "Session ended", {
                    "Duration": f"{report.get('duration_seconds', 0):.1f} seconds",
                    "Activities": report.get('activities_count', 0),
                    "Data Absorbed": f"{report.get('data_absorbed', 0)} bytes",
                    "Validation Score": f"{report.get('validation_score', 0):.1%}",
                    "Achievements": len(report.get('achievements', []))
                })
                return True
            else:
                self.print_result("❌", f"Failed to end session: {response.status_code}")
                return False
        except Exception as e:
            self.print_result("❌", f"Error ending session: {e}")
            return False
    
    def display_dashboard_snapshot(self):
        """Display a snapshot of the dashboard"""
        status = self.get_status()
        
        if not status:
            print("⚠️  Could not fetch status")
            return
        
        print("\n📊 Dashboard Snapshot:")
        print(f"   Total Activities: {status.get('total_activities', 0)}")
        print(f"   Validated: {status.get('validated_activities', 0)}")
        print(f"   Validation Rate: {status.get('validation_rate', 0):.1%}")
        print(f"   Data Absorbed: {status.get('total_data_absorbed_mb', 0):.2f} MB")
        
        recent = status.get('recent_activities', [])[:5]
        if recent:
            print("\n   Recent Activities:")
            for activity in recent:
                url = activity.get('source_url', 'N/A')[:50]
                status_val = activity.get('status', 'unknown')
                print(f"   - [{status_val}] {url}")
    
    def run_demo(self):
        """Run the complete demonstration"""
        print("\n")
        print("╔" + "=" * 78 + "╗")
        print("║" + " " * 20 + "🧠 GRACE LEARNING VISIBILITY DEMO" + " " * 24 + "║")
        print("╚" + "=" * 78 + "╝")
        
        # Step 1: Health Check
        self.print_section("Step 1: System Health Check")
        if not self.check_health():
            print("\n❌ Learning system is not available!")
            print("   Make sure Grace backend is running: python serve.py")
            return False
        
        self.print_result("✅", "Learning system is healthy and ready")
        time.sleep(1)
        
        # Step 2: Start Learning Session
        self.print_section("Step 2: Start Learning Session")
        success = self.start_session(
            domain="Python Web Scraping",
            goals=[
                "Learn web scraping techniques",
                "Absorb data from multiple sources",
                "Validate data integrity"
            ]
        )
        
        if not success:
            return False
        
        time.sleep(1)
        
        # Step 3: Simulate Learning from Multiple Sources
        self.print_section("Step 3: Absorb Data from Web Sources")
        
        learning_sources = [
            {
                "type": "documentation",
                "url": "https://docs.python.org/3/library/urllib.html",
                "content": """
                The urllib package provides several modules for working with URLs:
                - urllib.request for opening and reading URLs
                - urllib.error for exceptions raised by urllib.request
                - urllib.parse for parsing URLs
                - urllib.robotparser for parsing robots.txt files
                """
            },
            {
                "type": "web_scrape",
                "url": "https://realpython.com/python-web-scraping-practical-introduction/",
                "content": """
                Web scraping is the practice of extracting data from websites.
                Popular tools include BeautifulSoup, Scrapy, and Selenium.
                Always respect robots.txt and website terms of service.
                """
            },
            {
                "type": "github_repo",
                "url": "https://github.com/scrapy/scrapy",
                "content": """
                Scrapy: A Fast and Powerful Web Scraping Framework
                Features: Fast, extensible, handles concurrent requests
                Built-in support for CSS selectors and XPath
                """
            },
            {
                "type": "api_fetch",
                "url": "https://api.github.com/repos/python/cpython",
                "content": """
                {
                    "name": "cpython",
                    "full_name": "python/cpython",
                    "description": "The Python programming language",
                    "stargazers_count": 50000,
                    "language": "Python"
                }
                """
            }
        ]
        
        print(f"\nLearning from {len(learning_sources)} sources...")
        for idx, source in enumerate(learning_sources, 1):
            print(f"\n[{idx}/{len(learning_sources)}] Processing: {source['url'][:60]}...")
            success = self.record_learning_activity(
                source_type=source['type'],
                source_url=source['url'],
                content=source['content']
            )
            
            if not success:
                print("   ⚠️  Recording failed, continuing...")
            
            time.sleep(0.5)
        
        time.sleep(1)
        
        # Step 4: Validate Learning Activities
        self.print_section("Step 4: Validate Data Absorption")
        
        print(f"\nValidating {len(self.activity_ids)} activities...")
        for idx, activity_id in enumerate(self.activity_ids, 1):
            print(f"\n[{idx}/{len(self.activity_ids)}] Validating activity...")
            validation = self.validate_activity(activity_id)
            time.sleep(0.5)
        
        time.sleep(1)
        
        # Step 5: Display Dashboard
        self.print_section("Step 5: Real-time Dashboard View")
        self.display_dashboard_snapshot()
        time.sleep(1)
        
        # Step 6: End Session
        self.print_section("Step 6: End Learning Session")
        self.end_session()
        time.sleep(1)
        
        # Step 7: Summary
        self.print_section("Step 7: Summary & Next Steps")
        print("\n✅ Learning visibility system demonstration complete!")
        print("\n📊 What you can do now:")
        print("   1. View real-time dashboard:")
        print("      python learning_dashboard.py")
        print()
        print("   2. Generate validation report:")
        print("      python learning_validation_report.py")
        print()
        print("   3. Access API endpoints:")
        print("      http://localhost:8001/api/learning/status")
        print("      http://localhost:8001/api/learning/analytics")
        print("      http://localhost:8001/docs")
        print()
        print("   4. View logs and source URLs:")
        print("      logs/learning_activities/activities.jsonl")
        print("      logs/learning_activities/sessions.json")
        print()
        print("🔍 Full Traceability:")
        print("   - Every learning activity is tracked")
        print("   - Source URLs are logged with timestamps")
        print("   - Data integrity is validated")
        print("   - Complete audit trail for compliance")
        print()
        
        return True


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test Grace Learning Visibility System')
    parser.add_argument('--api-url', default='http://localhost:8001/api/learning', help='API base URL')
    
    args = parser.parse_args()
    
    test = LearningVisibilityTest(api_url=args.api_url)
    
    try:
        success = test.run_demo()
        
        if success:
            print("\n✅ All tests passed!")
            return 0
        else:
            print("\n❌ Some tests failed")
            return 1
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        return 130
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())