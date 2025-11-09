"""
Proactive Improvement Engine
Grace autonomously identifies and proposes improvements
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging

from .grace_self_analysis import grace_self_analysis
from .grace_log_reader import grace_log_reader
from .healing_analytics import healing_analytics
from .unified_logger import unified_logger
from .governance_framework import governance_framework
from .trigger_mesh import trigger_mesh, TriggerEvent

logger = logging.getLogger(__name__)


class ProactiveImprovementEngine:
    """
    Grace proactively identifies opportunities for improvement
    and proposes changes to enhance her own capabilities
    """
    
    def __init__(self):
        self.improvement_cycle_interval = 3600  # 1 hour
        self.running = False
        self.improvements_proposed = 0
        self.improvements_implemented = 0
        self.cycle_task = None
    
    async def start(self):
        """Start proactive improvement cycles"""
        if self.running:
            return
        
        self.running = True
        self.cycle_task = asyncio.create_task(self._improvement_loop())
        
        logger.info("[PROACTIVE] 🎯 Proactive Improvement Engine started")
    
    async def stop(self):
        """Stop proactive improvement"""
        self.running = False
        if self.cycle_task:
            self.cycle_task.cancel()
        logger.info("[PROACTIVE] Proactive Improvement Engine stopped")
    
    async def _improvement_loop(self):
        """Continuous improvement cycle"""
        
        while self.running:
            try:
                await asyncio.sleep(self.improvement_cycle_interval)
                
                logger.info("[PROACTIVE] 🔍 Running improvement analysis...")
                
                # Analyze performance
                analysis = await grace_self_analysis.analyze_performance(hours=24)
                
                # Identify improvement opportunities
                opportunities = await self._identify_opportunities(analysis)
                
                if opportunities:
                    logger.info(f"[PROACTIVE] 💡 Found {len(opportunities)} improvement opportunities")
                    
                    # Propose improvements
                    for opportunity in opportunities:
                        await self._propose_improvement(opportunity)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[PROACTIVE] Error in improvement cycle: {e}", exc_info=True)
    
    async def _identify_opportunities(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify improvement opportunities from analysis"""
        
        opportunities = []
        
        # Check healing success rate
        healing_perf = analysis.get('healing_performance', {})
        if healing_perf.get('success_rate', 1.0) < 0.85:
            opportunities.append({
                'type': 'enhance_healing',
                'priority': 'high',
                'description': 'Healing success rate below target',
                'current_value': healing_perf.get('success_rate', 0),
                'target_value': 0.9,
                'proposed_action': 'Add more error patterns to pattern library',
                'estimated_impact': 'Increase success rate by 10-15%'
            })
        
        # Check ML confidence
        learning_perf = analysis.get('learning_performance', {})
        if learning_perf.get('confidence', 1.0) < 0.75:
            opportunities.append({
                'type': 'improve_ml_confidence',
                'priority': 'medium',
                'description': 'ML prediction confidence below target',
                'current_value': learning_perf.get('confidence', 0),
                'target_value': 0.8,
                'proposed_action': 'Gather more training samples for ML models',
                'estimated_impact': 'Better error predictions'
            })
        
        # Check for improvement areas
        for area in analysis.get('improvement_areas', []):
            if 'recurring' in area.lower():
                opportunities.append({
                    'type': 'fix_recurring_error',
                    'priority': 'high',
                    'description': area,
                    'proposed_action': 'Create specialized handler for recurring pattern',
                    'estimated_impact': 'Reduce error recurrence'
                })
        
        # Check autonomous execution rate
        auto_perf = analysis.get('autonomous_performance', {})
        exec_rate = auto_perf.get('execution_rate', 0)
        if exec_rate < 0.8 and auto_perf.get('decisions_made', 0) > 10:
            opportunities.append({
                'type': 'improve_execution',
                'priority': 'medium',
                'description': 'Low execution rate - many decisions not executed',
                'current_value': exec_rate,
                'target_value': 0.9,
                'proposed_action': 'Review blocked decisions and adjust governance',
                'estimated_impact': 'More autonomous actions'
            })
        
        return opportunities
    
    async def _propose_improvement(self, opportunity: Dict[str, Any]):
        """Propose an improvement to the user"""
        
        self.improvements_proposed += 1
        
        # Check governance
        approval = await governance_framework.check_action(
            actor='grace_proactive',
            action='propose_improvement',
            resource=opportunity['type'],
            context=opportunity,
            confidence=0.8
        )
        
        # Create improvement proposal
        proposal = {
            'proposal_id': f"improve_{datetime.utcnow().timestamp()}",
            'opportunity': opportunity,
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'proposed',
            'approval_required': True
        }
        
        # Log proposal
        await unified_logger.log_agentic_spine_decision(
            decision_type='improvement_proposed',
            decision_context=opportunity,
            chosen_action=opportunity['proposed_action'],
            rationale=opportunity['description'],
            actor='proactive_improvement',
            confidence=0.8,
            risk_score=0.2,
            status='proposed',
            resource=opportunity['type']
        )
        
        # Publish event
        trigger_mesh.publish(TriggerEvent(
            event_type='improvement.proposed',
            source='proactive_improvement',
            actor='grace',
            resource=opportunity['type'],
            payload=proposal,
            timestamp=datetime.utcnow()
        ))
        
        logger.info(f"[PROACTIVE] 💡 Proposed improvement: {opportunity['description']}")
    
    async def get_status(self) -> Dict[str, Any]:
        """Get proactive improvement status"""
        return {
            'running': self.running,
            'cycle_interval_hours': self.improvement_cycle_interval / 3600,
            'improvements_proposed': self.improvements_proposed,
            'improvements_implemented': self.improvements_implemented
        }


# Global instance
proactive_improvement = ProactiveImprovementEngine()
