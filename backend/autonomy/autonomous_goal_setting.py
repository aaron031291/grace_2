"""
Autonomous Goal-Setting Engine
Grace sets her own goals based on performance analysis, user needs, and system evolution
"""

import asyncio
from typing import Dict, Any, List
from datetime import datetime, timedelta
import logging

from .models import async_session, Goal
from .goal_models import GoalEvaluation
from .grace_self_analysis import grace_self_analysis
from .unified_logger import unified_logger
from .governance_framework import governance_framework
from .trigger_mesh import trigger_mesh, TriggerEvent
from sqlalchemy import select, func

logger = logging.getLogger(__name__)


class AutonomousGoalSetting:
    """
    Grace autonomously creates, tracks, and evaluates her own goals
    based on performance data, user interactions, and system needs
    """
    
    def __init__(self):
        self.goal_cycle_interval = 86400  # 24 hours
        self.running = False
        self.goals_created = 0
        self.cycle_task = None
    
    async def start(self):
        """Start autonomous goal-setting cycles"""
        if self.running:
            return
        
        self.running = True
        self.cycle_task = asyncio.create_task(self._goal_setting_loop())
        
        logger.info("[GOAL-SETTING] 🎯 Autonomous Goal-Setting Engine started")
    
    async def stop(self):
        """Stop goal-setting"""
        self.running = False
        if self.cycle_task:
            self.cycle_task.cancel()
        logger.info("[GOAL-SETTING] Autonomous Goal-Setting Engine stopped")
    
    async def _goal_setting_loop(self):
        """Continuous goal-setting and evaluation cycle"""
        
        while self.running:
            try:
                await asyncio.sleep(self.goal_cycle_interval)
                
                logger.info("[GOAL-SETTING] 🔍 Running goal analysis...")
                
                # Evaluate existing goals
                await self._evaluate_existing_goals()
                
                # Create new goals based on analysis
                await self._create_autonomous_goals()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[GOAL-SETTING] Error in goal cycle: {e}", exc_info=True)
    
    async def _evaluate_existing_goals(self):
        """Evaluate progress on existing goals"""
        
        async with async_session() as session:
            # Get all active goals
            result = await session.execute(
                select(Goal).where(Goal.status.in_(['pending', 'active', 'in_progress']))
            )
            active_goals = result.scalars().all()
            
            logger.info(f"[GOAL-SETTING] Evaluating {len(active_goals)} active goals")
            
            for goal in active_goals:
                evaluation = await self._evaluate_goal(goal)
                
                # Create evaluation record
                goal_eval = GoalEvaluation(
                    goal_id=goal.id,
                    status=evaluation['status'],
                    explanation=evaluation['explanation'],
                    confidence=evaluation['confidence']
                )
                session.add(goal_eval)
                
                # Update goal status if completed
                if evaluation['status'] == 'met':
                    goal.status = 'completed'
                    goal.progress = 100
                    logger.info(f"[GOAL-SETTING] ✅ Goal completed: {goal.title}")
                elif evaluation['status'] == 'off_track':
                    logger.warning(f"[GOAL-SETTING] ⚠️ Goal off track: {goal.title}")
                
                # Log evaluation
                await unified_logger.log_agentic_spine_decision(
                    decision_type='goal_evaluation',
                    decision_context={'goal_id': goal.id, 'goal_title': goal.title},
                    chosen_action=evaluation['status'],
                    rationale=evaluation['explanation'],
                    actor='autonomous_goal_setting',
                    confidence=evaluation['confidence'],
                    risk_score=0.1,
                    status='completed',
                    resource=f"goal_{goal.id}"
                )
            
            await session.commit()
    
    async def _evaluate_goal(self, goal: Goal) -> Dict[str, Any]:
        """Evaluate a single goal's progress"""
        
        # Get relevant metrics based on goal type
        if 'healing' in goal.title.lower():
            analysis = await grace_self_analysis.analyze_performance(hours=24)
            success_rate = analysis.get('healing_performance', {}).get('success_rate', 0)
            
            if success_rate >= 0.9:
                return {
                    'status': 'met',
                    'explanation': f'Healing success rate is {success_rate:.2%}',
                    'confidence': 0.9
                }
            elif success_rate >= 0.8:
                return {
                    'status': 'on_track',
                    'explanation': f'Healing success rate is {success_rate:.2%}, progressing well',
                    'confidence': 0.8
                }
            else:
                return {
                    'status': 'at_risk',
                    'explanation': f'Healing success rate only {success_rate:.2%}',
                    'confidence': 0.7
                }
        
        elif 'learning' in goal.title.lower():
            analysis = await grace_self_analysis.analyze_performance(hours=24)
            learning_perf = analysis.get('learning_performance', {})
            confidence = learning_perf.get('confidence', 0)
            
            if confidence >= 0.85:
                return {
                    'status': 'met',
                    'explanation': f'ML confidence at {confidence:.2%}',
                    'confidence': 0.85
                }
            elif confidence >= 0.7:
                return {
                    'status': 'on_track',
                    'explanation': f'ML confidence improving: {confidence:.2%}',
                    'confidence': 0.75
                }
            else:
                return {
                    'status': 'at_risk',
                    'explanation': f'ML confidence low: {confidence:.2%}',
                    'confidence': 0.6
                }
        
        # Default evaluation based on deadline
        if goal.deadline:
            days_remaining = (goal.deadline - datetime.utcnow()).days
            if days_remaining < 0:
                return {
                    'status': 'off_track',
                    'explanation': 'Deadline passed',
                    'confidence': 0.9
                }
            elif days_remaining < 7:
                return {
                    'status': 'at_risk',
                    'explanation': f'Only {days_remaining} days remaining',
                    'confidence': 0.8
                }
        
        return {
            'status': 'on_track',
            'explanation': 'No issues detected',
            'confidence': 0.7
        }
    
    async def _create_autonomous_goals(self):
        """Create new goals based on system analysis"""
        
        logger.info("[GOAL-SETTING] 🎯 Analyzing system to set new goals...")
        
        # Analyze system performance
        analysis = await grace_self_analysis.analyze_performance(hours=168)  # 7 days
        
        # Identify goal opportunities
        goal_opportunities = await self._identify_goal_opportunities(analysis)
        
        if not goal_opportunities:
            logger.info("[GOAL-SETTING] No new goals needed at this time")
            return
        
        logger.info(f"[GOAL-SETTING] 💡 Identified {len(goal_opportunities)} potential new goals")
        
        # Create goals
        for opportunity in goal_opportunities:
            await self._create_goal(opportunity)
    
    async def _identify_goal_opportunities(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify opportunities for new goals"""
        
        opportunities = []
        
        # Goal: Improve healing success rate
        healing_perf = analysis.get('healing_performance', {})
        success_rate = healing_perf.get('success_rate', 1.0)
        if success_rate < 0.9:
            opportunities.append({
                'title': 'Improve Self-Healing Success Rate to 90%',
                'description': f'Current success rate is {success_rate:.2%}. Aim to improve error detection and fix strategies.',
                'category': 'performance',
                'priority': 'high',
                'metrics': {
                    'current': success_rate,
                    'target': 0.9
                },
                'deadline_days': 30
            })
        
        # Goal: Expand ML learning coverage
        learning_perf = analysis.get('learning_performance', {})
        patterns_learned = learning_perf.get('patterns_learned', 0)
        if patterns_learned < 50:
            opportunities.append({
                'title': 'Learn 50 Error Patterns',
                'description': f'Currently learned {patterns_learned} patterns. Expand pattern library to handle more error types.',
                'category': 'learning',
                'priority': 'medium',
                'metrics': {
                    'current': patterns_learned,
                    'target': 50
                },
                'deadline_days': 60
            })
        
        # Goal: Increase autonomous execution
        auto_perf = analysis.get('autonomous_performance', {})
        execution_rate = auto_perf.get('execution_rate', 0)
        if execution_rate < 0.85:
            opportunities.append({
                'title': 'Increase Autonomous Execution Rate to 85%',
                'description': f'Current execution rate is {execution_rate:.2%}. Build trust through consistent, safe actions.',
                'category': 'autonomy',
                'priority': 'high',
                'metrics': {
                    'current': execution_rate,
                    'target': 0.85
                },
                'deadline_days': 45
            })
        
        # Goal: Reduce response time
        avg_response = analysis.get('response_times', {}).get('avg_seconds', 0)
        if avg_response > 2.0:
            opportunities.append({
                'title': 'Reduce Average Response Time to Under 2s',
                'description': f'Current average response time is {avg_response:.1f}s. Optimize processing pipeline.',
                'category': 'performance',
                'priority': 'medium',
                'metrics': {
                    'current': avg_response,
                    'target': 2.0
                },
                'deadline_days': 30
            })
        
        # Goal: Comprehensive testing coverage
        opportunities.append({
            'title': 'Achieve 80% Test Coverage',
            'description': 'Implement comprehensive integration and unit tests across all systems.',
            'category': 'quality',
            'priority': 'high',
            'metrics': {
                'current': 0,
                'target': 80
            },
            'deadline_days': 90
        })
        
        return opportunities
    
    async def _create_goal(self, opportunity: Dict[str, Any]):
        """Create a new goal from an opportunity"""
        
        # Check governance approval
        approval = await governance_framework.check_action(
            actor='grace_autonomous_goals',
            action='create_goal',
            resource='goal_system',
            context=opportunity,
            confidence=0.8
        )
        
        if not approval.get('decision') == 'allow':
            logger.info(f"[GOAL-SETTING] 🚫 Goal creation blocked: {opportunity['title']}")
            return
        
        # Create deadline
        deadline = None
        if opportunity.get('deadline_days'):
            deadline = datetime.utcnow() + timedelta(days=opportunity['deadline_days'])
        
        # Create goal
        async with async_session() as session:
            goal = Goal(
                title=opportunity['title'],
                description=opportunity['description'],
                category=opportunity.get('category', 'general'),
                status='pending',
                priority=opportunity.get('priority', 'medium'),
                created_by='grace_autonomous',
                deadline=deadline,
                progress=0,
                auto_created=True
            )
            
            session.add(goal)
            await session.commit()
            await session.refresh(goal)
            
            self.goals_created += 1
            
            logger.info(f"[GOAL-SETTING] ✨ Created new goal: {goal.title}")
            
            # Log goal creation
            await unified_logger.log_agentic_spine_decision(
                decision_type='goal_created',
                decision_context=opportunity,
                chosen_action='create_goal',
                rationale=opportunity['description'],
                actor='autonomous_goal_setting',
                confidence=0.8,
                risk_score=0.1,
                status='completed',
                resource=f"goal_{goal.id}"
            )
            
            # Publish event
            await trigger_mesh.publish(TriggerEvent(
                event_type='goal.created',
                source='autonomous_goal_setting',
                actor='grace',
                resource=f"goal_{goal.id}",
                payload={'goal': opportunity},
                timestamp=datetime.utcnow()
            ))
    
    async def get_status(self) -> Dict[str, Any]:
        """Get goal-setting system status"""
        
        async with async_session() as session:
            # Count goals by status
            result = await session.execute(
                select(func.count(Goal.id)).where(Goal.status == 'active')
            )
            active_goals = result.scalar() or 0
            
            result = await session.execute(
                select(func.count(Goal.id)).where(Goal.status == 'completed')
            )
            completed_goals = result.scalar() or 0
            
            result = await session.execute(
                select(func.count(Goal.id)).where(Goal.auto_created == True)
            )
            autonomous_goals = result.scalar() or 0
        
        return {
            'running': self.running,
            'cycle_interval_hours': self.goal_cycle_interval / 3600,
            'goals_created': self.goals_created,
            'active_goals': active_goals,
            'completed_goals': completed_goals,
            'autonomous_goals': autonomous_goals
        }


# Global instance
autonomous_goal_setting = AutonomousGoalSetting()
