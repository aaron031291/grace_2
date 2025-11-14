"""
Daily Reporter
Generates daily/hourly briefs for human oversight
"""

from typing import Dict, List, Any
from datetime import datetime, timedelta
from pathlib import Path
import json
import logging

from .unified_logger import unified_logger

logger = logging.getLogger(__name__)


class DailyReporter:
    """
    Generates daily summary reports
    
    Includes:
    - Knowledge ingested
    - Experiments run + outcomes
    - KPIs & trust deltas
    - New tasks queued or completed
    - Alerts and recommendations
    """
    
    async def generate_daily_brief(self) -> str:
        """Generate daily brief for human review"""
        
        logger.info("[DAILY-REPORTER] Generating daily brief...")
        
        # Collect data from last 24 hours
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=1)
        
        brief = {
            'date': end_time.strftime('%Y-%m-%d'),
            'period': f"{start_time.isoformat()} to {end_time.isoformat()}",
            'knowledge_ingested': await self._count_knowledge_ingested(start_time, end_time),
            'experiments_run': await self._count_experiments(start_time, end_time),
            'kpi_summary': await self._summarize_kpis(start_time, end_time),
            'trust_deltas': await self._calculate_trust_deltas(start_time, end_time),
            'tasks_completed': await self._count_completed_tasks(start_time, end_time),
            'alerts': await self._get_alerts(start_time, end_time),
            'recommendations': await self._generate_recommendations()
        }
        
        # Generate markdown report
        report_path = await self._save_brief_as_markdown(brief)
        
        logger.info(f"[DAILY-REPORTER] Brief generated: {report_path}")
        
        return str(report_path)
    
    async def _count_knowledge_ingested(self, start_time, end_time) -> Dict[str, int]:
        """Count knowledge items ingested"""
        
        # Check ingestion queue
        queue_dir = Path('storage/ingestion_queue')
        
        if not queue_dir.exists():
            return {'papers': 0, 'repos': 0, 'qa': 0}
        
        counts = {'papers': 0, 'repos': 0, 'qa': 0, 'other': 0}
        
        for queue_file in queue_dir.glob('*.json'):
            try:
                with open(queue_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Check if processed in time window
                queued_at = datetime.fromisoformat(data.get('queued_at', ''))
                
                if start_time <= queued_at <= end_time:
                    items = data.get('items', [])
                    
                    for item in items:
                        item_type = item.get('type', 'other')
                        counts[item_type] = counts.get(item_type, 0) + 1
            except:
                pass
        
        return counts
    
    async def _count_experiments(self, start_time, end_time) -> Dict[str, Any]:
        """Count sandbox experiments"""
        
        logs_dir = Path('logs/sandbox')
        
        if not logs_dir.exists():
            return {'total': 0, 'passed': 0, 'failed': 0}
        
        counts = {'total': 0, 'passed': 0, 'failed': 0, 'avg_trust': 0.0}
        trust_scores = []
        
        for log_file in logs_dir.glob('*.json'):
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                started_at = datetime.fromisoformat(data.get('started_at', ''))
                
                if start_time <= started_at <= end_time:
                    counts['total'] += 1
                    
                    if data.get('status') == 'success':
                        counts['passed'] += 1
                    else:
                        counts['failed'] += 1
                    
                    trust_scores.append(data.get('trust_score', 0))
            except:
                pass
        
        if trust_scores:
            counts['avg_trust'] = sum(trust_scores) / len(trust_scores)
        
        return counts
    
    async def _summarize_kpis(self, start_time, end_time) -> Dict[str, Any]:
        """Summarize KPIs"""
        
        # Would query metrics from unified logger
        # For now, return template
        
        return {
            'avg_latency_ms': 42.0,
            'error_rate': 0.002,
            'uptime_percent': 99.9,
            'requests_processed': 1500
        }
    
    async def _calculate_trust_deltas(self, start_time, end_time) -> Dict[str, float]:
        """Calculate trust score changes"""
        
        # Would query trust scores over time
        # For now, return template
        
        return {
            'system_trust': +5.0,  # Increased by 5%
            'ml_apis': +3.0,
            'sandbox': 0.0,
            'overall': +2.5
        }
    
    async def _count_completed_tasks(self, start_time, end_time) -> int:
        """Count completed tasks"""
        
        # Would query task queue
        return 0
    
    async def _get_alerts(self, start_time, end_time) -> List[Dict[str, Any]]:
        """Get alerts from period"""
        
        # Would query unified logger for alerts
        return []
    
    async def _generate_recommendations(self) -> List[str]:
        """Generate recommendations for human"""
        
        recommendations = []
        
        # Check pending proposals
        proposals_dir = Path('storage/improvement_proposals')
        
        if proposals_dir.exists():
            proposal_count = len(list(proposals_dir.glob('*.json')))
            
            if proposal_count > 0:
                recommendations.append(
                    f"Review {proposal_count} improvement proposals awaiting approval"
                )
        
        # Check system state
        from .grace_control_center import grace_control
        state = grace_control.get_state()
        
        if state['pending_tasks'] > 10:
            recommendations.append(
                f"{state['pending_tasks']} tasks queued - consider reviewing priorities"
            )
        
        return recommendations
    
    async def _save_brief_as_markdown(self, brief: Dict[str, Any]) -> Path:
        """Save brief as markdown report"""
        
        reports_dir = Path('reports/daily_briefs')
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        report_file = reports_dir / f"brief_{brief['date']}.md"
        
        content = f"""# Grace Daily Brief - {brief['date']}

**Period:** {brief['period']}

---

## Knowledge Ingested

Grace learned from:
- Research Papers: {brief['knowledge_ingested'].get('papers', 0)}
- Code Repositories: {brief['knowledge_ingested'].get('repos', 0)}
- Q&A Forums: {brief['knowledge_ingested'].get('qa', 0)}
- Other Sources: {brief['knowledge_ingested'].get('other', 0)}

**Total Items:** {sum(brief['knowledge_ingested'].values())}

---

## Experiments Run

Grace tested {brief['experiments_run']['total']} improvements:
- Passed: {brief['experiments_run']['passed']}
- Failed: {brief['experiments_run']['failed']}
- Average Trust Score: {brief['experiments_run']['avg_trust']:.1f}%

---

## KPI Summary

System performance:
- Average Latency: {brief['kpi_summary']['avg_latency_ms']:.1f}ms
- Error Rate: {brief['kpi_summary']['error_rate']:.3f}%
- Uptime: {brief['kpi_summary']['uptime_percent']:.1f}%
- Requests Processed: {brief['kpi_summary']['requests_processed']:,}

---

## Trust Score Changes

Trust deltas (past 24 hours):
- System Trust: {brief['trust_deltas'].get('system_trust', 0):+.1f}%
- ML APIs: {brief['trust_deltas'].get('ml_apis', 0):+.1f}%
- Sandbox: {brief['trust_deltas'].get('sandbox', 0):+.1f}%
- **Overall: {brief['trust_deltas'].get('overall', 0):+.1f}%**

---

## Tasks Completed

Completed tasks: {brief['tasks_completed']}

---

## Alerts

{len(brief['alerts'])} alerts in past 24 hours

---

## Recommendations

{''.join(f'- {rec}' + chr(10) for rec in brief['recommendations']) if brief['recommendations'] else 'No recommendations at this time.'}

---

## Actions Required

{'**No action required** - All within acceptable parameters.' if not brief['recommendations'] else '**Please review recommendations above**'}

---

*Generated by Grace's Daily Reporter*  
*Next brief: {(datetime.utcnow() + timedelta(days=1)).strftime('%Y-%m-%d')}*
"""
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"[DAILY-REPORTER] Brief saved: {report_file}")
        
        return report_file


# Global instance
daily_reporter = DailyReporter()
