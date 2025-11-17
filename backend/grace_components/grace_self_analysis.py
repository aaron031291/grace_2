"""
Grace Self-Analysis Engine
Grace analyzes her own performance, identifies improvement areas, and sets goals
"""

from typing import Dict, Any, List
from datetime import datetime
import logging

from .grace_log_reader import grace_log_reader
from .healing_analytics import healing_analytics
from .unified_logger import unified_logger

logger = logging.getLogger(__name__)


class GraceSelfAnalysis:
    """
    Grace's self-analysis and introspection capability
    Allows her to understand her performance and improve
    """
    
    async def analyze_performance(self, hours: int = 24) -> Dict[str, Any]:
        """Analyze Grace's performance over time period"""
        
        # Get raw data
        activity = await grace_log_reader.get_my_recent_activity(hours)
        healing_summary = await healing_analytics.get_healing_summary(hours)
        ml_stats = await healing_analytics.get_ml_learning_stats(hours)
        errors = await grace_log_reader.get_my_errors(hours, limit=10)
        successes = await grace_log_reader.get_my_successes(hours, limit=10)
        learning = await grace_log_reader.get_my_learning_progress()
        
        # Calculate performance metrics
        analysis = {
            'period_hours': hours,
            'timestamp': datetime.utcnow().isoformat(),
            
            # Overall health score (0-100)
            'health_score': self._calculate_health_score(healing_summary, ml_stats, activity),
            
            # Performance breakdown
            'healing_performance': {
                'success_rate': healing_summary['success_rate'],
                'total_fixes': healing_summary['total_attempts'],
                'grade': self._grade_performance(healing_summary['success_rate'])
            },
            
            'learning_performance': {
                'patterns_learned': learning['patterns_learned'],
                'predictions_made': ml_stats['predictions_made'],
                'confidence': ml_stats['average_confidence'],
                'grade': self._grade_performance(ml_stats['average_confidence'])
            },
            
            'autonomous_performance': {
                'decisions_made': activity['decisions']['made'],
                'actions_executed': activity['decisions']['executed'],
                'execution_rate': activity['decisions']['executed'] / activity['decisions']['made'] if activity['decisions']['made'] > 0 else 0,
                'grade': 'A' if activity['decisions']['made'] > 0 else 'N/A'
            },
            
            # Improvement areas
            'improvement_areas': self._identify_improvement_areas(errors, healing_summary, ml_stats),
            
            # Strengths
            'strengths': self._identify_strengths(successes, healing_summary, ml_stats),
            
            # Goals
            'current_goals': self._set_goals(healing_summary, ml_stats, learning),
            
            # Trending
            'trending': 'improving'  # Would calculate actual trend
        }
        
        # Log self-analysis
        await unified_logger.log_agentic_spine_decision(
            decision_type='self_analysis',
            decision_context={'period_hours': hours},
            chosen_action='analyzed_performance',
            rationale=f"Health score: {analysis['health_score']}/100",
            actor='grace_self_analysis',
            confidence=0.9,
            risk_score=0.0,
            outcome='completed',
            impact={'health_score': analysis['health_score']}
        )
        
        return analysis
    
    def _calculate_health_score(self, healing: Dict, ml: Dict, activity: Dict) -> int:
        """Calculate overall health score (0-100)"""
        
        # Healing success rate (40% of score)
        healing_score = healing.get('success_rate', 0.0) * 40
        
        # ML confidence (30% of score)
        ml_score = ml.get('average_confidence', 0.0) * 30
        
        # Activity level (30% of score)
        activity_score = min(activity['decisions']['made'] / 10, 1.0) * 30
        
        total = healing_score + ml_score + activity_score
        
        return int(total)
    
    def _grade_performance(self, rate: float) -> str:
        """Convert rate to letter grade"""
        if rate >= 0.9:
            return 'A'
        elif rate >= 0.8:
            return 'B'
        elif rate >= 0.7:
            return 'C'
        elif rate >= 0.6:
            return 'D'
        else:
            return 'F'
    
    def _identify_improvement_areas(self, errors: List, healing: Dict, ml: Dict) -> List[str]:
        """Identify areas needing improvement"""
        areas = []
        
        # Check healing success rate
        if healing.get('success_rate', 1.0) < 0.8:
            areas.append("Healing success rate below 80% - need better error patterns")
        
        # Check ML confidence
        if ml.get('average_confidence', 1.0) < 0.7:
            areas.append("ML confidence low - need more training data")
        
        # Check for recurring errors
        error_types = {}
        for err in errors:
            et = err['error_type']
            error_types[et] = error_types.get(et, 0) + 1
        
        for error_type, count in error_types.items():
            if count > 2:
                areas.append(f"Recurring {error_type} errors - pattern not learned yet")
        
        return areas
    
    def _identify_strengths(self, successes: List, healing: Dict, ml: Dict) -> List[str]:
        """Identify what Grace does well"""
        strengths = []
        
        # Check healing success rate
        if healing.get('success_rate', 0.0) >= 0.8:
            strengths.append(f"High healing success rate ({healing['success_rate']:.1%})")
        
        # Check ML confidence
        if ml.get('average_confidence', 0.0) >= 0.7:
            strengths.append(f"Strong ML predictions ({ml['average_confidence']:.1%} confidence)")
        
        # Check common successful fixes
        success_types = {}
        for suc in successes:
            et = suc['error_type']
            success_types[et] = success_types.get(et, 0) + 1
        
        for error_type, count in success_types.items():
            if count > 2:
                strengths.append(f"Excellent at fixing {error_type} ({count} successes)")
        
        return strengths
    
    def _set_goals(self, healing: Dict, ml: Dict, learning: Dict) -> List[Dict[str, Any]]:
        """Set improvement goals for Grace"""
        goals = []
        
        # Healing success rate goal
        current_rate = healing.get('success_rate', 0.0)
        if current_rate < 0.9:
            goals.append({
                'area': 'healing',
                'current': current_rate,
                'target': 0.9,
                'action': 'Learn more error patterns and fix strategies'
            })
        
        # ML learning goal
        current_patterns = learning.get('patterns_learned', 0)
        if current_patterns < 20:
            goals.append({
                'area': 'ml_learning',
                'current': current_patterns,
                'target': 20,
                'action': 'Encounter and learn more diverse error patterns'
            })
        
        # ML confidence goal
        current_confidence = ml.get('average_confidence', 0.0)
        if current_confidence < 0.8:
            goals.append({
                'area': 'ml_confidence',
                'current': current_confidence,
                'target': 0.8,
                'action': 'Gather more training data for better predictions'
            })
        
        return goals
    
    async def generate_improvement_plan(self) -> str:
        """Generate improvement plan based on analysis"""
        
        analysis = await self.analyze_performance(hours=24)
        
        plan = "🎯 MY IMPROVEMENT PLAN\n\n"
        
        plan += f"Health Score: {analysis['health_score']}/100\n\n"
        
        # Current performance
        plan += "📊 Current Performance:\n"
        plan += f"   • Healing: {analysis['healing_performance']['grade']} ({analysis['healing_performance']['success_rate']:.1%})\n"
        plan += f"   • Learning: {analysis['learning_performance']['grade']} (confidence: {analysis['learning_performance']['confidence']:.1%})\n"
        plan += f"   • Autonomy: {analysis['autonomous_performance']['grade']}\n\n"
        
        # Strengths
        if analysis['strengths']:
            plan += "💪 My Strengths:\n"
            for strength in analysis['strengths']:
                plan += f"   • {strength}\n"
            plan += "\n"
        
        # Improvement areas
        if analysis['improvement_areas']:
            plan += "🎯 Areas to Improve:\n"
            for area in analysis['improvement_areas']:
                plan += f"   • {area}\n"
            plan += "\n"
        
        # Goals
        if analysis['current_goals']:
            plan += "🏁 My Goals:\n"
            for goal in analysis['current_goals']:
                plan += f"   • {goal['area']}: {goal['current']} → {goal['target']}\n"
                plan += f"     Action: {goal['action']}\n"
            plan += "\n"
        
        # Next steps
        plan += "📋 Next Steps:\n"
        if analysis['improvement_areas']:
            plan += f"   1. Focus on {analysis['improvement_areas'][0]}\n"
            if len(analysis['improvement_areas']) > 1:
                plan += f"   2. Address {analysis['improvement_areas'][1]}\n"
        else:
            plan += "   1. Continue current excellent performance\n"
            plan += "   2. Explore new error patterns to expand knowledge\n"
        
        return plan


# Global instance
grace_self_analysis = GraceSelfAnalysis()
