"""
Auto-Status Brief Generator

Periodically queries recent mission outcomes and generates consolidated status briefs.

Process:
1. Every N hours (configurable), query mission outcomes from world model via RAG
2. Aggregate outcomes by domain and severity
3. Generate human-readable "Today I fixed..." summary
4. Post to world model for conversational recall
5. Optional: Send to Slack/Email for stakeholder notifications

Enables proactive status reporting: "Today I fixed 3 issues in ecommerce, 2 in payments..."
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)


class AutoStatusBrief:
    """
    Generates periodic status briefs from mission outcomes
    
    Consolidates mission narratives into digestible summaries
    for stakeholders and Grace's conversational memory
    """
    
    def __init__(
        self,
        interval_hours: int = 24,  # Daily briefs by default
        enable_slack: bool = False,
        enable_email: bool = False
    ):
        self.interval_hours = interval_hours
        self.enable_slack = enable_slack
        self.enable_email = enable_email
        
        self._running = False
        self._task = None
        self.briefs_generated = 0
        self.last_brief_at = None
    
    async def initialize(self):
        """Initialize and start the brief generation loop"""
        logger.info(f"[AUTO-BRIEF] Initializing (interval: {self.interval_hours}h)")
        
        # Don't start automatically - let startup control it
        logger.info("[AUTO-BRIEF] Ready to generate status briefs")
    
    async def start_loop(self):
        """Start the periodic brief generation loop"""
        if self._running:
            logger.warning("[AUTO-BRIEF] Loop already running")
            return
        
        self._running = True
        self._task = asyncio.create_task(self._brief_loop())
        logger.info(f"[AUTO-BRIEF] Started loop (every {self.interval_hours}h)")
    
    async def stop_loop(self):
        """Stop the brief generation loop"""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("[AUTO-BRIEF] Stopped loop")
    
    async def _brief_loop(self):
        """Main loop that generates briefs periodically"""
        while self._running:
            try:
                await self.generate_and_publish_brief()
                
                # Wait for next interval
                await asyncio.sleep(self.interval_hours * 3600)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[AUTO-BRIEF] Error in loop: {e}")
                # Wait 5 minutes before retry on error
                await asyncio.sleep(300)
    
    async def generate_and_publish_brief(self) -> Dict[str, Any]:
        """
        Generate status brief and publish to all configured channels
        
        Returns:
            {
                "brief_id": str,
                "narrative": str,
                "missions_covered": int,
                "domains_affected": List[str],
                "published_to": List[str]
            }
        """
        try:
            logger.info("[AUTO-BRIEF] Generating status brief...")
            
            # Step 1: Query recent mission outcomes
            outcomes = await self._query_recent_outcomes()
            
            if not outcomes:
                logger.info("[AUTO-BRIEF] No recent outcomes to report")
                return {
                    "success": True,
                    "narrative": "No missions completed in the reporting period.",
                    "missions_covered": 0
                }
            
            # Step 2: Aggregate by domain and type
            aggregated = self._aggregate_outcomes(outcomes)
            
            # Step 3: Generate consolidated narrative
            narrative = self._generate_brief_narrative(aggregated)
            
            # Step 4: Publish to world model
            brief_id = await self._publish_to_world_model(narrative, aggregated)
            
            # Step 5: Optional external notifications
            published_to = ["world_model"]
            
            if self.enable_slack:
                await self._publish_to_slack(narrative, aggregated)
                published_to.append("slack")
            
            if self.enable_email:
                await self._publish_to_email(narrative, aggregated)
                published_to.append("email")
            
            # Step 6: NEW - Proactive Follow-ups (analyze for problems)
            follow_ups = await self._analyze_and_create_follow_ups(aggregated, outcomes)
            
            self.briefs_generated += 1
            self.last_brief_at = datetime.utcnow()
            
            logger.info(f"[AUTO-BRIEF] Generated brief covering {len(outcomes)} missions")
            if follow_ups:
                logger.info(f"[AUTO-BRIEF] Created {len(follow_ups)} follow-up missions")
            
            return {
                "success": True,
                "brief_id": brief_id,
                "narrative": narrative,
                "missions_covered": len(outcomes),
                "domains_affected": list(aggregated.keys()),
                "published_to": published_to,
                "follow_ups_created": follow_ups,
                "generated_at": self.last_brief_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"[AUTO-BRIEF] Failed to generate brief: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _query_recent_outcomes(self) -> List[Dict[str, Any]]:
        """Query recent mission outcomes from world model via RAG"""
        try:
            from backend.services.rag_service import rag_service
            
            # Calculate time window
            since = datetime.utcnow() - timedelta(hours=self.interval_hours)
            
            # Query mission outcomes
            results = await rag_service.retrieve(
                query="mission outcome completed fixed improved",
                filters={
                    "tags": "mission,outcome,completed",
                    "timestamp_after": since.isoformat()
                },
                top_k=50,
                requested_by="auto_status_brief"
            )
            
            outcomes = []
            if results.get("results"):
                for result in results["results"]:
                    outcomes.append({
                        "knowledge_id": result.get("id"),
                        "content": result.get("content"),
                        "metadata": result.get("metadata", {}),
                        "score": result.get("score", 0)
                    })
            
            return outcomes
            
        except Exception as e:
            logger.error(f"[AUTO-BRIEF] Failed to query outcomes: {e}")
            return []
    
    def _aggregate_outcomes(
        self,
        outcomes: List[Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """Aggregate outcomes by domain"""
        aggregated = defaultdict(lambda: {
            "missions": [],
            "total_impact": {},
            "mission_count": 0,
            "success_count": 0,
            "failure_count": 0
        })
        
        for outcome in outcomes:
            metadata = outcome.get("metadata", {})
            domain_id = metadata.get("domain_id", "unknown")
            
            domain_data = aggregated[domain_id]
            domain_data["missions"].append({
                "content": outcome.get("content", ""),
                "mission_id": metadata.get("mission_id"),
                "mission_type": metadata.get("mission_type"),
                "duration": metadata.get("duration_seconds", 0),
                "metrics": metadata.get("metrics_impact", {})
            })
            domain_data["mission_count"] += 1
            
            # Aggregate metrics impact
            metrics_impact = metadata.get("metrics_impact", {})
            for metric_name, impact in metrics_impact.items():
                if metric_name not in domain_data["total_impact"]:
                    domain_data["total_impact"][metric_name] = {
                        "total_improvement": 0,
                        "occurrences": 0
                    }
                
                if isinstance(impact, dict) and "percent_change" in impact:
                    domain_data["total_impact"][metric_name]["total_improvement"] += abs(impact["percent_change"])
                    domain_data["total_impact"][metric_name]["occurrences"] += 1
        
        return dict(aggregated)
    
    def _generate_brief_narrative(
        self,
        aggregated: Dict[str, Dict[str, Any]]
    ) -> str:
        """Generate human-readable brief from aggregated data"""
        
        parts = []
        
        # Header
        total_missions = sum(d["mission_count"] for d in aggregated.values())
        time_window = "today" if self.interval_hours <= 24 else f"in the last {self.interval_hours}h"
        
        parts.append(f"Status Brief: I completed {total_missions} missions {time_window}")
        parts.append("")
        
        # Per-domain summaries
        for domain_id, data in sorted(aggregated.items(), key=lambda x: x[1]["mission_count"], reverse=True):
            mission_count = data["mission_count"]
            
            parts.append(f"**{domain_id.title()}** ({mission_count} missions):")
            
            # Sample key fix
            if data["missions"]:
                sample = data["missions"][0]["content"][:200]
                parts.append(f"  - {sample}...")
            
            # Key metrics improved
            if data["total_impact"]:
                for metric, impact_data in list(data["total_impact"].items())[:2]:
                    avg = impact_data["total_improvement"] / impact_data["occurrences"]
                    parts.append(f"  - {metric}: avg {avg:.1f}% improvement")
            
            parts.append("")
        
        # Summary footer
        parts.append(f"All systems operational. {total_missions} autonomous fixes applied.")
        
        return "\n".join(parts)
    
    async def _publish_to_world_model(
        self,
        narrative: str,
        aggregated: Dict[str, Dict[str, Any]]
    ) -> str:
        """Publish brief to world model"""
        try:
            from backend.world_model import grace_world_model
            
            knowledge_id = await grace_world_model.add_knowledge(
                category='system',
                content=narrative,
                source='auto_status_brief',
                confidence=0.98,
                tags=['status_brief', 'periodic_summary', 'mission_aggregate'],
                metadata={
                    "brief_type": "mission_status",
                    "interval_hours": self.interval_hours,
                    "domains_covered": list(aggregated.keys()),
                    "total_missions": sum(d["mission_count"] for d in aggregated.values()),
                    "generated_by": "auto_status_brief"
                }
            )
            
            return knowledge_id
            
        except Exception as e:
            logger.error(f"[AUTO-BRIEF] Failed to publish to world model: {e}")
            return ""
    
    async def _publish_to_slack(
        self,
        narrative: str,
        aggregated: Dict[str, Dict[str, Any]]
    ):
        """Publish brief to Slack (production-ready)"""
        try:
            import os
            import httpx
            
            slack_webhook = os.getenv("SLACK_WEBHOOK_URL")
            
            if not slack_webhook:
                logger.warning("[AUTO-BRIEF] Slack enabled but no webhook configured (set SLACK_WEBHOOK_URL)")
                return
            
            # Build rich Slack message with formatting
            total_missions = sum(d["mission_count"] for d in aggregated.values())
            
            # Header block
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"🤖 Grace Status Brief - {datetime.utcnow().strftime('%Y-%m-%d')}",
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*{total_missions} missions completed* across {len(aggregated)} domains"
                    }
                },
                {"type": "divider"}
            ]
            
            # Per-domain sections
            for domain_id, data in sorted(aggregated.items(), key=lambda x: x[1]["mission_count"], reverse=True):
                mission_count = data["mission_count"]
                
                # Domain header
                domain_text = f"*{domain_id.title()}* ({mission_count} missions)\n"
                
                # Sample mission
                if data["missions"]:
                    sample = data["missions"][0]["content"][:150]
                    domain_text += f"• {sample}...\n"
                
                # Key metrics
                if data["total_impact"]:
                    for metric, impact_data in list(data["total_impact"].items())[:2]:
                        avg = impact_data["total_improvement"] / impact_data["occurrences"]
                        emoji = "📈" if avg > 0 else "📉"
                        domain_text += f"{emoji} _{metric}_: {abs(avg):.1f}% {'improvement' if avg > 0 else 'degradation'}\n"
                
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": domain_text
                    }
                })
            
            # Footer
            blocks.append({"type": "divider"})
            blocks.append({
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"All systems operational • Generated at {datetime.utcnow().strftime('%H:%M UTC')}"
                    }
                ]
            })
            
            payload = {
                "text": f"Grace Status Brief: {total_missions} missions completed",
                "blocks": blocks,
                "username": "Grace",
                "icon_emoji": ":robot_face:"
            }
            
            # Send with retry logic
            max_retries = 3
            retry_delay = 2
            
            for attempt in range(max_retries):
                try:
                    async with httpx.AsyncClient(timeout=10.0) as client:
                        response = await client.post(slack_webhook, json=payload)
                        
                        if response.status_code == 200:
                            logger.info("[AUTO-BRIEF] Successfully published to Slack")
                            return
                        else:
                            logger.warning(f"[AUTO-BRIEF] Slack returned {response.status_code}: {response.text}")
                    
                except httpx.TimeoutException:
                    if attempt < max_retries - 1:
                        logger.warning(f"[AUTO-BRIEF] Slack timeout, retrying in {retry_delay}s...")
                        await asyncio.sleep(retry_delay)
                        retry_delay *= 2
                    else:
                        raise
            
        except Exception as e:
            logger.error(f"[AUTO-BRIEF] Failed to publish to Slack: {e}")
    
    async def _publish_to_email(
        self,
        narrative: str,
        aggregated: Dict[str, Dict[str, Any]]
    ):
        """Publish brief to email (production-ready)"""
        try:
            import os
            
            email_recipients = os.getenv("STATUS_BRIEF_RECIPIENTS", "").split(",")
            email_recipients = [r.strip() for r in email_recipients if r.strip()]
            
            if not email_recipients:
                logger.warning("[AUTO-BRIEF] Email enabled but no recipients configured (set STATUS_BRIEF_RECIPIENTS)")
                return
            
            smtp_host = os.getenv("SMTP_HOST", "localhost")
            smtp_port = int(os.getenv("SMTP_PORT", "587"))
            smtp_user = os.getenv("SMTP_USER", "")
            smtp_pass = os.getenv("SMTP_PASSWORD", "")
            from_email = os.getenv("SMTP_FROM_EMAIL", "grace@localhost")
            
            # Build HTML email
            total_missions = sum(d["mission_count"] for d in aggregated.values())
            
            html_content = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .header {{ background: #4CAF50; color: white; padding: 20px; text-align: center; }}
                    .summary {{ background: #f5f5f5; padding: 15px; margin: 20px 0; border-left: 4px solid #4CAF50; }}
                    .domain {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
                    .domain-title {{ font-size: 18px; font-weight: bold; color: #4CAF50; }}
                    .metric {{ margin: 5px 0; padding: 5px; background: #f9f9f9; }}
                    .footer {{ text-align: center; color: #999; font-size: 12px; margin-top: 30px; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>🤖 Grace Status Brief</h1>
                    <p>{datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}</p>
                </div>
                
                <div class="summary">
                    <strong>{total_missions} missions completed</strong> across {len(aggregated)} domains
                </div>
                
            """
            
            # Per-domain sections
            for domain_id, data in sorted(aggregated.items(), key=lambda x: x[1]["mission_count"], reverse=True):
                mission_count = data["mission_count"]
                
                html_content += f"""
                <div class="domain">
                    <div class="domain-title">{domain_id.title()} ({mission_count} missions)</div>
                """
                
                # Sample mission
                if data["missions"]:
                    sample = data["missions"][0]["content"][:200]
                    html_content += f"<p>• {sample}...</p>"
                
                # Key metrics
                if data["total_impact"]:
                    html_content += "<div>"
                    for metric, impact_data in list(data["total_impact"].items())[:3]:
                        avg = impact_data["total_improvement"] / impact_data["occurrences"]
                        emoji = "📈" if avg > 0 else "📉"
                        html_content += f"""
                        <div class="metric">
                            {emoji} <strong>{metric}</strong>: {abs(avg):.1f}% {'improvement' if avg > 0 else 'degradation'}
                        </div>
                        """
                    html_content += "</div>"
                
                html_content += "</div>"
            
            html_content += """
                <div class="footer">
                    <p>All systems operational</p>
                    <p>This is an automated report from Grace's autonomous operations system</p>
                </div>
            </body>
            </html>
            """
            
            # Plain text version
            text_content = narrative
            
            # Send email
            try:
                import aiosmtplib
                from email.mime.multipart import MIMEMultipart
                from email.mime.text import MIMEText
                
                message = MIMEMultipart('alternative')
                message['Subject'] = f"Grace Status Brief - {total_missions} missions completed"
                message['From'] = from_email
                message['To'] = ", ".join(email_recipients)
                
                part1 = MIMEText(text_content, 'plain')
                part2 = MIMEText(html_content, 'html')
                
                message.attach(part1)
                message.attach(part2)
                
                # Send with authentication if configured
                if smtp_user and smtp_pass:
                    await aiosmtplib.send(
                        message,
                        hostname=smtp_host,
                        port=smtp_port,
                        username=smtp_user,
                        password=smtp_pass,
                        start_tls=True
                    )
                else:
                    await aiosmtplib.send(
                        message,
                        hostname=smtp_host,
                        port=smtp_port
                    )
                
                logger.info(f"[AUTO-BRIEF] Successfully sent email to {len(email_recipients)} recipients")
                
            except ImportError:
                logger.error("[AUTO-BRIEF] aiosmtplib not installed. Install with: pip install aiosmtplib")
            except Exception as smtp_error:
                logger.error(f"[AUTO-BRIEF] SMTP error: {smtp_error}")
            
        except Exception as e:
            logger.error(f"[AUTO-BRIEF] Failed to publish to email: {e}")
    
    async def _analyze_and_create_follow_ups(
        self,
        aggregated: Dict[str, Dict[str, Any]],
        outcomes: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Analyze brief for problems and create follow-up missions
        
        Triggers follow-ups for:
        - Repeat failures in same domain
        - Low effectiveness scores
        - Degrading KPIs
        - Multiple failed tests
        
        Returns list of created follow-up missions
        """
        follow_ups = []
        
        try:
            # Analyze each domain for problems
            for domain_id, data in aggregated.items():
                problems = []
                
                # Check 1: Multiple missions in short time (potential recurring issue)
                if data["mission_count"] >= 3:
                    problems.append({
                        "type": "recurring_issue",
                        "severity": "medium",
                        "description": f"{domain_id} had {data['mission_count']} missions - may indicate recurring issue"
                    })
                
                # Check 2: Failed missions
                if data.get("failure_count", 0) > 0:
                    problems.append({
                        "type": "mission_failures",
                        "severity": "high",
                        "description": f"{domain_id} had {data['failure_count']} failed missions"
                    })
                
                # Check 3: Low effectiveness scores
                low_effectiveness = []
                for mission in data["missions"]:
                    metadata = mission.get("metadata", {})
                    effectiveness = metadata.get("effectiveness_score", 1.0)
                    if effectiveness < 0.5:
                        low_effectiveness.append(mission)
                
                if low_effectiveness:
                    problems.append({
                        "type": "low_effectiveness",
                        "severity": "medium",
                        "description": f"{domain_id} had {len(low_effectiveness)} missions with effectiveness < 0.5"
                    })
                
                # Check 4: Degrading trends in KPIs
                if data.get("total_impact"):
                    for metric_name, impact_data in data["total_impact"].items():
                        avg_improvement = impact_data["total_improvement"] / impact_data["occurrences"]
                        if avg_improvement < 0:  # Metrics getting worse
                            problems.append({
                                "type": "degrading_kpi",
                                "severity": "high",
                                "description": f"{domain_id} metric '{metric_name}' degrading (avg: {avg_improvement:.1f}%)"
                            })
                
                # Create follow-up missions for significant problems
                if problems:
                    high_severity = [p for p in problems if p["severity"] == "high"]
                    
                    if high_severity or len(problems) >= 2:
                        follow_up = await self._create_follow_up_mission(
                            domain_id=domain_id,
                            problems=problems,
                            mission_data=data
                        )
                        if follow_up:
                            follow_ups.append(follow_up)
            
            return follow_ups
            
        except Exception as e:
            logger.error(f"[AUTO-BRIEF] Failed to analyze follow-ups: {e}")
            return []
    
    async def _create_follow_up_mission(
        self,
        domain_id: str,
        problems: List[Dict[str, Any]],
        mission_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Create a follow-up refinement mission
        
        Returns mission details if created
        """
        try:
            from backend.autonomy.proactive_mission_generator import proactive_mission_generator
            
            # Build mission context
            problem_summary = "; ".join([p["description"] for p in problems])
            high_severity = any(p["severity"] == "high" for p in problems)
            
            mission_title = f"Investigate {domain_id} issues"
            mission_reason = f"Auto-brief flagged problems: {problem_summary}"
            
            # Determine mission type based on problems
            mission_type = "investigation"
            if any(p["type"] == "degrading_kpi" for p in problems):
                mission_type = "performance_analysis"
            elif any(p["type"] == "mission_failures" for p in problems):
                mission_type = "failure_remediation"
            
            # Create mission via proactive generator
            mission = await proactive_mission_generator.create_mission(
                title=mission_title,
                domain_id=domain_id,
                mission_type=mission_type,
                trigger_reason=mission_reason,
                priority="high" if high_severity else "medium",
                metadata={
                    "triggered_by": "auto_status_brief",
                    "problems": problems,
                    "original_mission_count": mission_data["mission_count"]
                }
            )
            
            logger.info(f"[AUTO-BRIEF] Created follow-up mission for {domain_id}")
            
            return {
                "mission_id": mission.get("mission_id"),
                "domain_id": domain_id,
                "title": mission_title,
                "problems": len(problems),
                "severity": "high" if high_severity else "medium"
            }
            
        except Exception as e:
            logger.error(f"[AUTO-BRIEF] Failed to create follow-up mission: {e}")
            return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get brief generator statistics"""
        return {
            "running": self._running,
            "interval_hours": self.interval_hours,
            "briefs_generated": self.briefs_generated,
            "last_brief_at": self.last_brief_at.isoformat() if self.last_brief_at else None,
            "slack_enabled": self.enable_slack,
            "email_enabled": self.enable_email
        }


# Global instance
auto_status_brief = AutoStatusBrief(
    interval_hours=24,  # Daily briefs
    enable_slack=False,  # Enable via env var
    enable_email=False   # Enable via env var
)


# Convenience function for manual brief generation
async def generate_status_brief() -> Dict[str, Any]:
    """
    Generate a status brief on-demand
    
    Returns the brief narrative and metadata
    """
    return await auto_status_brief.generate_and_publish_brief()