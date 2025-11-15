"""
Learning Validation Report Generator
Comprehensive reports showing what Grace learned, from where, with full traceability
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path


class LearningValidationReport:
    """Generate detailed validation reports for Grace's learning activities"""
    
    def __init__(self, api_url: str = "http://localhost:8001/api/learning"):
        self.api_url = api_url
        self.report_dir = Path("reports/learning_validation")
        self.report_dir.mkdir(parents=True, exist_ok=True)
    
    def fetch_status(self) -> Dict[str, Any]:
        """Fetch current learning status"""
        try:
            response = requests.get(f"{self.api_url}/status", timeout=10)
            if response.status_code == 200:
                return response.json().get('data', {})
            return {}
        except Exception as e:
            print(f"Error fetching status: {e}")
            return {}
    
    def fetch_analytics(self) -> Dict[str, Any]:
        """Fetch analytics data"""
        try:
            response = requests.get(f"{self.api_url}/analytics", timeout=10)
            if response.status_code == 200:
                return response.json().get('data', {})
            return {}
        except Exception as e:
            print(f"Error fetching analytics: {e}")
            return {}
    
    def fetch_validation_report(self, hours: int = 24) -> Dict[str, Any]:
        """Fetch validation report"""
        try:
            response = requests.get(f"{self.api_url}/report/validation?hours={hours}", timeout=10)
            if response.status_code == 200:
                return response.json().get('data', {})
            return {}
        except Exception as e:
            print(f"Error fetching validation report: {e}")
            return {}
    
    def generate_markdown_report(self, hours: int = 24) -> str:
        """Generate a detailed markdown report"""
        timestamp = datetime.now()
        
        status = self.fetch_status()
        analytics = self.fetch_analytics()
        validation = self.fetch_validation_report(hours)
        
        report = []
        report.append("# Grace Learning Validation Report")
        report.append(f"**Generated:** {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"**Period:** Last {hours} hours")
        report.append("")
        
        # Executive Summary
        report.append("## 📊 Executive Summary")
        report.append("")
        total_activities = status.get('total_activities', 0)
        validated = status.get('validated_activities', 0)
        validation_rate = status.get('validation_rate', 0)
        total_data_mb = status.get('total_data_absorbed_mb', 0)
        
        report.append(f"- **Total Learning Activities:** {total_activities:,}")
        report.append(f"- **Successfully Validated:** {validated:,}")
        report.append(f"- **Validation Success Rate:** {validation_rate:.1%}")
        report.append(f"- **Total Data Absorbed:** {total_data_mb:.2f} MB")
        report.append(f"- **Active Sessions:** {status.get('sessions_count', 0)}")
        report.append("")
        
        # Learning Velocity
        report.append("## ⚡ Learning Velocity")
        report.append("")
        rates = status.get('current_learning_rate', {})
        report.append(f"- Last 5 minutes: {rates.get('last_5_min', 0)} activities")
        report.append(f"- Last 15 minutes: {rates.get('last_15_min', 0)} activities")
        report.append(f"- Last hour: {rates.get('last_hour', 0)} activities")
        report.append(f"- Last 24 hours: {rates.get('last_24h', 0)} activities")
        report.append("")
        
        # Data Sources with Links
        report.append("## 📚 Learning Sources & URLs")
        report.append("")
        report.append("Complete traceability of all learning sources:")
        report.append("")
        
        recent_activities = status.get('recent_activities', [])
        if recent_activities:
            report.append("### Recent Activities (With Source URLs)")
            report.append("")
            report.append("| Timestamp | Source Type | Source URL | Status | Size | Validation |")
            report.append("|-----------|-------------|------------|--------|------|------------|")
            
            for activity in recent_activities[:50]:  # Include more for full traceability
                timestamp = activity.get('timestamp', 'N/A')[:19]
                source_type = activity.get('source_type', 'unknown').replace('_', ' ').title()
                source_url = activity.get('source_url', 'N/A')
                status_val = activity.get('status', 'unknown')
                size_kb = activity.get('size_kb', 0)
                validation_score = activity.get('validation_score', 0)
                score_display = f"{validation_score:.1%}" if validation_score > 0 else "Pending"
                
                # Truncate URL for table, full URL in separate section
                url_display = source_url[:60] + "..." if len(source_url) > 60 else source_url
                
                report.append(f"| {timestamp} | {source_type} | {url_display} | {status_val} | {size_kb:.1f} KB | {score_display} |")
            
            report.append("")
            
            # Full URLs section
            report.append("### Complete Source URLs")
            report.append("")
            report.append("Full list of all source URLs accessed during this period:")
            report.append("")
            
            unique_urls = {}
            for activity in recent_activities:
                url = activity.get('source_url', '')
                if url and url not in unique_urls:
                    source_type = activity.get('source_type', 'unknown')
                    unique_urls[url] = source_type
            
            for idx, (url, source_type) in enumerate(sorted(unique_urls.items()), 1):
                report.append(f"{idx}. **{source_type.replace('_', ' ').title()}:** `{url}`")
            
            report.append("")
        
        # Source Breakdown
        report.append("## 📈 Source Type Breakdown")
        report.append("")
        source_breakdown = status.get('source_breakdown', {})
        
        if source_breakdown:
            total_from_sources = sum(source_breakdown.values())
            report.append("| Source Type | Count | Percentage |")
            report.append("|-------------|-------|------------|")
            
            for source, count in sorted(source_breakdown.items(), key=lambda x: x[1], reverse=True):
                source_name = source.replace('_', ' ').title()
                percentage = (count / total_from_sources * 100) if total_from_sources > 0 else 0
                report.append(f"| {source_name} | {count} | {percentage:.1f}% |")
            
            report.append("")
        
        # Validation Details
        if validation:
            report.append("## ✅ Validation Details")
            report.append("")
            summary = validation.get('summary', {})
            report.append(f"- **Success Rate:** {summary.get('success_rate', 0):.1%}")
            report.append(f"- **Average Validation Score:** {summary.get('avg_validation_score', 0):.1%}")
            report.append(f"- **Failed Activities:** {summary.get('failed_activities', 0)}")
            report.append("")
            
            # Source Performance
            source_perf = validation.get('source_performance', {})
            if source_perf:
                report.append("### Source Performance")
                report.append("")
                report.append("| Source Type | Total | Validated | Success Rate | Data (MB) |")
                report.append("|-------------|-------|-----------|--------------|-----------|")
                
                for source, perf in sorted(source_perf.items(), key=lambda x: x[1]['success_rate'], reverse=True):
                    source_name = source.replace('_', ' ').title()
                    total = perf.get('total', 0)
                    validated = perf.get('validated', 0)
                    success_rate = perf.get('success_rate', 0)
                    data_mb = perf.get('total_data_mb', 0)
                    
                    report.append(f"| {source_name} | {total} | {validated} | {success_rate:.1%} | {data_mb:.2f} |")
                
                report.append("")
        
        # Analytics Deep Dive
        if analytics and 'message' not in analytics:
            report.append("## 📊 Analytics Deep Dive")
            report.append("")
            
            # Time period
            period = analytics.get('period', {})
            if period:
                start = period.get('start', 'N/A')[:19]
                end = period.get('end', 'N/A')[:19]
                duration = period.get('duration_hours', 0)
                report.append(f"**Analysis Period:** {start} to {end} ({duration:.1f} hours)")
                report.append("")
            
            # Data Volume
            data_volume = analytics.get('data_volume', {})
            if data_volume:
                report.append("### Data Volume Statistics")
                report.append("")
                report.append(f"- Total Bytes: {data_volume.get('total_bytes', 0):,}")
                report.append(f"- Total MB: {data_volume.get('total_mb', 0):.2f}")
                report.append(f"- Total GB: {data_volume.get('total_gb', 0):.3f}")
                report.append(f"- Average per Activity: {data_volume.get('avg_per_activity_kb', 0):.2f} KB")
                report.append("")
            
            # Learning Velocity
            velocity = analytics.get('learning_velocity', {})
            if velocity:
                report.append("### Learning Velocity Metrics")
                report.append("")
                report.append(f"- Activities per Hour: {velocity.get('activities_per_hour', 0):.2f}")
                report.append(f"- MB per Hour: {velocity.get('mb_per_hour', 0):.2f}")
                report.append("")
        
        # Active Session Info
        active_session = status.get('active_session')
        if active_session:
            report.append("## 🔄 Active Learning Session")
            report.append("")
            report.append(f"- **Session ID:** `{active_session.get('session_id', 'N/A')}`")
            report.append(f"- **Target Domain:** {active_session.get('target_domain', 'N/A')}")
            report.append(f"- **Started:** {active_session.get('started_at', 'N/A')[:19]}")
            report.append(f"- **Activities:** {len(active_session.get('activities', []))}")
            report.append(f"- **Data Absorbed:** {active_session.get('total_data_absorbed', 0):,} bytes")
            report.append(f"- **Validation Score:** {active_session.get('validation_score', 0):.1%}")
            report.append("")
            
            goals = active_session.get('goals', [])
            if goals:
                report.append("**Goals:**")
                for goal in goals:
                    report.append(f"- {goal}")
                report.append("")
            
            achievements = active_session.get('achievements', [])
            if achievements:
                report.append("**Achievements:**")
                for achievement in achievements:
                    report.append(f"- ✅ {achievement}")
                report.append("")
        
        # Health Status
        health = status.get('health', {})
        if health:
            report.append("## 🏥 System Health")
            report.append("")
            report.append(f"- Tracker Active: {health.get('tracker_active', False)}")
            report.append(f"- Last Activity: {health.get('last_activity', 'N/A')[:19]}")
            report.append(f"- Validation Health: {health.get('validation_health', 'unknown').upper()}")
            report.append("")
        
        # Alerts
        alerts = status.get('alerts', [])
        if alerts:
            report.append("## ⚠️ Alerts & Warnings")
            report.append("")
            for alert in alerts:
                severity = alert.get('severity', 'info').upper()
                message = alert.get('message', 'Unknown')
                emoji = {'ERROR': '🔴', 'WARNING': '🟡', 'INFO': '🔵'}.get(severity, '⚪')
                report.append(f"- {emoji} **{severity}:** {message}")
            report.append("")
        
        # Footer
        report.append("---")
        report.append("")
        report.append("## 📝 Notes")
        report.append("")
        report.append("- All learning activities are tracked with full source URL traceability")
        report.append("- Each activity undergoes validation to ensure data integrity")
        report.append("- Validation scores indicate the quality and completeness of absorbed data")
        report.append("- Source URLs are logged for audit compliance and debugging")
        report.append("")
        report.append("**Report Generated by Grace Learning Validation System**")
        report.append(f"Timestamp: {timestamp.isoformat()}")
        report.append("")
        
        return "\n".join(report)
    
    def generate_json_report(self, hours: int = 24) -> Dict[str, Any]:
        """Generate a JSON report with complete data"""
        timestamp = datetime.now()
        
        status = self.fetch_status()
        analytics = self.fetch_analytics()
        validation = self.fetch_validation_report(hours)
        
        # Extract all source URLs with metadata
        source_urls = []
        for activity in status.get('recent_activities', []):
            source_urls.append({
                'url': activity.get('source_url', ''),
                'source_type': activity.get('source_type', ''),
                'timestamp': activity.get('timestamp', ''),
                'status': activity.get('status', ''),
                'size_kb': activity.get('size_kb', 0),
                'validation_score': activity.get('validation_score', 0),
                'activity_id': activity.get('activity_id', '')
            })
        
        report = {
            'metadata': {
                'generated_at': timestamp.isoformat(),
                'period_hours': hours,
                'report_type': 'learning_validation'
            },
            'summary': {
                'total_activities': status.get('total_activities', 0),
                'validated_activities': status.get('validated_activities', 0),
                'validation_rate': status.get('validation_rate', 0),
                'total_data_absorbed_mb': status.get('total_data_absorbed_mb', 0),
                'sessions_count': status.get('sessions_count', 0)
            },
            'source_urls': source_urls,
            'source_breakdown': status.get('source_breakdown', {}),
            'learning_velocity': status.get('current_learning_rate', {}),
            'validation_details': validation,
            'analytics': analytics,
            'active_session': status.get('active_session'),
            'health': status.get('health', {}),
            'alerts': status.get('alerts', [])
        }
        
        return report
    
    def save_report(self, hours: int = 24, format: str = 'both') -> Dict[str, str]:
        """Save report to disk"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        saved_files = {}
        
        if format in ['markdown', 'both']:
            md_content = self.generate_markdown_report(hours)
            md_file = self.report_dir / f"validation_report_{timestamp}.md"
            md_file.write_text(md_content, encoding='utf-8')
            saved_files['markdown'] = str(md_file)
            print(f"✅ Markdown report saved: {md_file}")
        
        if format in ['json', 'both']:
            json_content = self.generate_json_report(hours)
            json_file = self.report_dir / f"validation_report_{timestamp}.json"
            json_file.write_text(json.dumps(json_content, indent=2), encoding='utf-8')
            saved_files['json'] = str(json_file)
            print(f"✅ JSON report saved: {json_file}")
        
        return saved_files
    
    def print_quick_summary(self):
        """Print a quick summary to console"""
        status = self.fetch_status()
        
        print("\n" + "=" * 80)
        print(" " * 20 + "🧠 GRACE LEARNING VALIDATION SUMMARY")
        print("=" * 80)
        print()
        
        print(f"Total Activities: {status.get('total_activities', 0):,}")
        print(f"Validated: {status.get('validated_activities', 0):,}")
        print(f"Validation Rate: {status.get('validation_rate', 0):.1%}")
        print(f"Data Absorbed: {status.get('total_data_absorbed_mb', 0):.2f} MB")
        print()
        
        print("Recent Source URLs:")
        for idx, activity in enumerate(status.get('recent_activities', [])[:10], 1):
            url = activity.get('source_url', 'N/A')
            source_type = activity.get('source_type', 'unknown')
            print(f"{idx}. [{source_type}] {url}")
        
        print()
        print("=" * 80)
        print()


def main():
    """Main entry point for generating reports"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate Grace Learning Validation Reports')
    parser.add_argument('--hours', type=int, default=24, help='Hours to look back (default: 24)')
    parser.add_argument('--format', choices=['markdown', 'json', 'both'], default='both', help='Report format')
    parser.add_argument('--summary-only', action='store_true', help='Print summary to console only')
    
    args = parser.parse_args()
    
    reporter = LearningValidationReport()
    
    if args.summary_only:
        reporter.print_quick_summary()
    else:
        print("\n🔍 Generating Learning Validation Report...")
        print(f"Period: Last {args.hours} hours")
        print(f"Format: {args.format}")
        print()
        
        saved = reporter.save_report(hours=args.hours, format=args.format)
        
        print()
        print("✅ Report generation complete!")
        print()
        print("Saved files:")
        for format_type, filepath in saved.items():
            print(f"  - {format_type.upper()}: {filepath}")
        print()


if __name__ == "__main__":
    main()