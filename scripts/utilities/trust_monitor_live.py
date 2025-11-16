#!/usr/bin/env python3
"""
TRUST Framework Live Monitor - PRODUCTION
Real-time monitoring of all TRUST systems with auto-refresh
"""

import asyncio
import httpx
import time
from datetime import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

API_BASE = "http://localhost:8000"
REFRESH_INTERVAL = 5  # seconds


class LiveMonitor:
    """Real-time TRUST framework monitor"""
    
    def __init__(self, api_base: str = API_BASE):
        self.api_base = api_base
        self.running = True
    
    async def run(self):
        """Run live monitoring loop"""
        
        print("\033[?25l")  # Hide cursor
        
        try:
            while self.running:
                await self._refresh_display()
                await asyncio.sleep(REFRESH_INTERVAL)
        
        except KeyboardInterrupt:
            print("\033[?25h")  # Show cursor
            print("\nMonitoring stopped.")
        
        finally:
            print("\033[?25h")  # Show cursor
    
    async def _refresh_display(self):
        """Refresh display with latest data"""
        
        # Clear screen
        print("\033[2J\033[H", end='')
        
        # Header
        print("=" * 80)
        print(" " * 20 + "GRACE TRUST FRAMEWORK - LIVE MONITOR")
        print("=" * 80)
        print(f"Last Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Refresh: Every {REFRESH_INTERVAL}s | Press Ctrl+C to exit")
        print("=" * 80)
        print()
        
        async with httpx.AsyncClient() as client:
            try:
                # Get dashboard
                response = await client.get(f"{self.api_base}/api/trust/dashboard", timeout=5)
                
                if response.status_code != 200:
                    print(f"[ERROR] API returned {response.status_code}")
                    print("Is Grace running? (python serve.py)")
                    return
                
                data = response.json()
                
                # Summary
                summary = data['summary']
                alerts = data['alerts']
                systems = data['systems_active']
                
                # Overall Health
                health_score = summary['overall_health_score']
                health_color = self._get_health_color(health_score)
                
                print(f"OVERALL HEALTH: {health_color}{health_score:.0%}\033[0m")
                print()
                
                # Models Status
                print(f"MODELS:")
                print(f"  Total:       {summary['total_models']}")
                print(f"  Healthy:     \033[92m{summary['healthy_models']}\033[0m")
                
                if summary['unhealthy_models'] > 0:
                    print(f"  Unhealthy:   \033[93m{summary['unhealthy_models']}\033[0m")
                
                if summary['quarantined_models'] > 0:
                    print(f"  Quarantined: \033[91m{summary['quarantined_models']}\033[0m")
                
                print()
                
                # Hallucinations
                print(f"HALLUCINATIONS:")
                print(f"  Total: {summary['total_hallucinations']}")
                print(f"  Models needing retraining: {summary['models_needing_retraining']}")
                print()
                
                # Active Systems
                print(f"ACTIVE SYSTEMS:")
                active_count = sum(1 for v in systems.values() if v)
                print(f"  {active_count}/{len(systems)} systems active")
                print()
                
                # Alerts
                if alerts['unhealthy_models']:
                    print("\033[93m[WARNING] Unhealthy Models:\033[0m")
                    for model in alerts['unhealthy_models'][:5]:
                        print(f"  - {model}")
                    if len(alerts['unhealthy_models']) > 5:
                        print(f"  ... and {len(alerts['unhealthy_models']) - 5} more")
                    print()
                
                if alerts['quarantined_models']:
                    print("\033[91m[CRITICAL] Quarantined Models:\033[0m")
                    for model in alerts['quarantined_models']:
                        print(f"  - {model}")
                    print()
                
                if alerts['high_risk_models']:
                    print("\033[91m[HIGH RISK] Models with High Hallucination Debt:\033[0m")
                    for model in alerts['high_risk_models'][:5]:
                        print(f"  - {model}")
                    print()
                
                # Retraining priorities
                if alerts['retraining_priorities']:
                    print("RETRAINING PRIORITIES (Top 5):")
                    for item in alerts['retraining_priorities'][:5]:
                        priority_color = "\033[91m" if item['priority'] >= 8 else "\033[93m" if item['priority'] >= 6 else "\033[0m"
                        print(f"  {priority_color}[{item['priority']}] {item['model']}\033[0m")
                    print()
                
                # Quick stats
                print("QUICK STATS:")
                
                # Get detailed stats
                status_response = await client.get(f"{self.api_base}/api/trust/status", timeout=5)
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    
                    # HTM stats
                    htm_stats = status_data['systems'].get('htm_anomaly_detection', {})
                    print(f"  HTM Detectors: {len(htm_stats)} active")
                    
                    # Verification stats
                    verify_stats = status_data['systems'].get('verification_mesh', {})
                    if verify_stats:
                        print(f"  Verifications: {verify_stats.get('total_verifications', 0)} (pass rate: {verify_stats.get('pass_rate', 0):.0%})")
                    
                    # Data hygiene
                    hygiene_stats = status_data['systems'].get('data_hygiene', {})
                    if hygiene_stats:
                        print(f"  Data Audits: {hygiene_stats.get('total_audits', 0)} (pass rate: {hygiene_stats.get('pass_rate', 0):.0%})")
                
                print()
                
                # Footer
                print("=" * 80)
                print("Commands: Ctrl+C to exit | Check logs: logs/ | API: /api/trust/dashboard")
                print("=" * 80)
            
            except Exception as e:
                print(f"[ERROR] Failed to fetch data: {e}")
                print()
                print("Make sure Grace is running: python serve.py")
    
    def _get_health_color(self, score: float) -> str:
        """Get ANSI color code for health score"""
        
        if score >= 0.9:
            return "\033[92m"  # Green
        elif score >= 0.7:
            return "\033[93m"  # Yellow
        else:
            return "\033[91m"  # Red


async def main():
    """Main entry point"""
    
    print("Starting TRUST Framework Live Monitor...")
    print(f"Connecting to {API_BASE}...")
    print()
    
    monitor = LiveMonitor()
    await monitor.run()


if __name__ == "__main__":
    asyncio.run(main())
