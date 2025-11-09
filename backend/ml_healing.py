"""
ML/DL-Enhanced Healing
Machine learning and deep learning for error prediction and fix optimization
"""

import asyncio
import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import logging

from .immutable_log import ImmutableLog
from .models import async_session
from .base_models import ImmutableLogEntry
from sqlalchemy import select, desc, and_

logger = logging.getLogger(__name__)


class MLHealingEngine:
    """
    Machine learning for autonomous healing
    - Predicts which errors are likely to occur
    - Learns which fixes work best
    - Optimizes healing strategies
    """
    
    def __init__(self):
        self.immutable_log = ImmutableLog()
        
        # Learning data
        self.error_patterns = defaultdict(lambda: {
            'count': 0,
            'fix_attempts': 0,
            'fix_successes': 0,
            'avg_time_to_fix': 0.0,
            'confidence': 0.0
        })
        
        self.fix_strategies = defaultdict(lambda: {
            'attempts': 0,
            'successes': 0,
            'success_rate': 0.0
        })
        
        # ML models (simplified - would use actual ML libraries)
        self.prediction_model = None
        self.optimization_model = None
        
        self.running = False
        self.learning_task = None
    
    async def start(self):
        """Start ML learning loop"""
        if self.running:
            return
        
        self.running = True
        
        # Load historical data
        await self._load_historical_patterns()
        
        # Start continuous learning
        self.learning_task = asyncio.create_task(self._learning_loop())
        
        logger.info("[ML_HEAL] 🧠 ML/DL Healing Engine started")
    
    async def stop(self):
        """Stop ML learning"""
        self.running = False
        if self.learning_task:
            self.learning_task.cancel()
        logger.info("[ML_HEAL] ML/DL Healing Engine stopped")
    
    async def _learning_loop(self):
        """Continuous learning from healing actions"""
        while self.running:
            try:
                await asyncio.sleep(300)  # Learn every 5 minutes
                
                logger.info("[ML_HEAL] 📚 Running learning cycle...")
                await self._update_patterns()
                await self._train_models()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[ML_HEAL] Learning error: {e}")
    
    async def _load_historical_patterns(self):
        """Load historical error and fix data"""
        try:
            async with async_session() as session:
                # Get all error detection events
                result = await session.execute(
                    select(ImmutableLogEntry)
                    .where(ImmutableLogEntry.action.like('%error%'))
                    .order_by(desc(ImmutableLogEntry.timestamp))
                    .limit(500)
                )
                
                error_entries = result.scalars().all()
                
                # Get all fix events
                result = await session.execute(
                    select(ImmutableLogEntry)
                    .where(ImmutableLogEntry.action.like('%fix%'))
                    .order_by(desc(ImmutableLogEntry.timestamp))
                    .limit(500)
                )
                
                fix_entries = result.scalars().all()
                
                logger.info(f"[ML_HEAL] Loaded {len(error_entries)} errors, {len(fix_entries)} fixes for learning")
                
                # Build pattern database
                for entry in error_entries:
                    pattern_key = self._extract_pattern_key(entry)
                    if pattern_key:
                        self.error_patterns[pattern_key]['count'] += 1
                
                # Correlate fixes with errors
                for fix_entry in fix_entries:
                    strategy_key = self._extract_strategy_key(fix_entry)
                    if strategy_key:
                        self.fix_strategies[strategy_key]['attempts'] += 1
                        
                        if fix_entry.result == 'success':
                            self.fix_strategies[strategy_key]['successes'] += 1
        
        except Exception as e:
            logger.error(f"[ML_HEAL] Error loading historical data: {e}")
    
    async def _update_patterns(self):
        """Update error patterns with new data"""
        try:
            # Calculate success rates
            for strategy_key, data in self.fix_strategies.items():
                if data['attempts'] > 0:
                    data['success_rate'] = data['successes'] / data['attempts']
            
            # Calculate confidence scores
            for pattern_key, data in self.error_patterns.items():
                # Simple confidence based on fix success rate
                if data['fix_attempts'] > 0:
                    data['confidence'] = data['fix_successes'] / data['fix_attempts']
                else:
                    data['confidence'] = 0.0
            
            logger.debug(f"[ML_HEAL] Updated {len(self.error_patterns)} error patterns")
        
        except Exception as e:
            logger.error(f"[ML_HEAL] Pattern update error: {e}")
    
    async def _train_models(self):
        """Train ML models for prediction and optimization"""
        try:
            # Simple ML: Calculate probabilities
            
            # Error prediction model (which errors likely to occur)
            error_frequencies = {}
            total_errors = sum(p['count'] for p in self.error_patterns.values())
            
            if total_errors > 0:
                for pattern_key, data in self.error_patterns.items():
                    error_frequencies[pattern_key] = data['count'] / total_errors
            
            self.prediction_model = {
                'type': 'frequency_based',
                'frequencies': error_frequencies,
                'trained_at': datetime.utcnow().isoformat()
            }
            
            # Fix optimization model (which fixes work best)
            self.optimization_model = {
                'type': 'success_rate_based',
                'strategies': dict(self.fix_strategies),
                'trained_at': datetime.utcnow().isoformat()
            }
            
            logger.info(f"[ML_HEAL] 🎯 Models trained: {len(error_frequencies)} error patterns")
        
        except Exception as e:
            logger.error(f"[ML_HEAL] Model training error: {e}")
    
    def _extract_pattern_key(self, entry: ImmutableLogEntry) -> Optional[str]:
        """Extract pattern identifier from error entry"""
        # Simple pattern extraction from action
        action = entry.action or ""
        
        if 'await' in action.lower():
            return 'incorrect_await'
        elif 'attribute' in action.lower():
            return 'missing_attribute'
        elif 'json' in action.lower() or 'serializ' in action.lower():
            return 'json_serialization'
        elif 'import' in action.lower() or 'module' in action.lower():
            return 'missing_module'
        
        return None
    
    def _extract_strategy_key(self, entry: ImmutableLogEntry) -> Optional[str]:
        """Extract fix strategy from fix entry"""
        action = entry.action or ""
        
        if 'remove' in action.lower() and 'await' in action.lower():
            return 'remove_await'
        elif 'add' in action.lower() and 'attribute' in action.lower():
            return 'add_attribute'
        elif 'serializ' in action.lower():
            return 'add_serialization'
        
        return None
    
    async def predict_error_likelihood(self, error_type: str) -> float:
        """Predict likelihood of error occurring (0.0-1.0)"""
        if not self.prediction_model:
            return 0.5  # Default
        
        frequencies = self.prediction_model.get('frequencies', {})
        return frequencies.get(error_type, 0.1)
    
    async def recommend_fix_strategy(self, error_type: str) -> Optional[Dict[str, Any]]:
        """Recommend best fix strategy based on past success"""
        if not self.optimization_model:
            return None
        
        strategies = self.optimization_model.get('strategies', {})
        
        # Find strategies that match this error type
        relevant_strategies = {}
        for strategy_key, data in strategies.items():
            if error_type in strategy_key or strategy_key in error_type:
                relevant_strategies[strategy_key] = data
        
        if not relevant_strategies:
            return None
        
        # Return strategy with highest success rate
        best_strategy = max(
            relevant_strategies.items(),
            key=lambda x: x[1]['success_rate']
        )
        
        return {
            'strategy': best_strategy[0],
            'success_rate': best_strategy[1]['success_rate'],
            'attempts': best_strategy[1]['attempts'],
            'confidence': 'high' if best_strategy[1]['success_rate'] > 0.7 else 'medium'
        }
    
    async def get_insights(self) -> Dict[str, Any]:
        """Get ML insights about error patterns and healing"""
        return {
            'error_patterns': dict(self.error_patterns),
            'fix_strategies': dict(self.fix_strategies),
            'prediction_model': self.prediction_model,
            'optimization_model': self.optimization_model,
            'total_patterns_learned': len(self.error_patterns),
            'total_strategies_learned': len(self.fix_strategies)
        }


class DLHealingEngine:
    """
    Deep learning for advanced healing
    - Pattern recognition in code
    - Code similarity matching
    - Fix generation refinement
    """
    
    def __init__(self):
        self.immutable_log = ImmutableLog()
        self.embeddings_cache = {}
        self.running = False
    
    async def start(self):
        """Start DL engine"""
        if self.running:
            return
        
        self.running = True
        logger.info("[DL_HEAL] 🧬 Deep Learning Healing Engine started")
    
    async def stop(self):
        """Stop DL engine"""
        self.running = False
        logger.info("[DL_HEAL] Deep Learning Healing Engine stopped")
    
    async def embed_code(self, code: str) -> List[float]:
        """Generate code embedding for similarity matching"""
        # Simplified - would use actual code embedding model
        # For now, use simple features
        features = [
            len(code),  # Length
            code.count('def '),  # Functions
            code.count('class '),  # Classes
            code.count('await '),  # Async operations
            code.count('import '),  # Imports
        ]
        
        # Normalize
        if sum(features) > 0:
            normalized = [f / sum(features) for f in features]
        else:
            normalized = [0.0] * len(features)
        
        return normalized
    
    async def find_similar_fixes(self, error_code: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Find similar code that was successfully fixed"""
        
        # Get code embedding
        query_embedding = await self.embed_code(error_code)
        
        # Search for similar fixes in history
        # (Simplified - would use vector database)
        
        async with async_session() as session:
            result = await session.execute(
                select(ImmutableLogEntry)
                .where(ImmutableLogEntry.action.like('%fix%'))
                .where(ImmutableLogEntry.result == 'success')
                .order_by(desc(ImmutableLogEntry.timestamp))
                .limit(limit)
            )
            
            entries = result.scalars().all()
            
            similar_fixes = []
            for entry in entries:
                similar_fixes.append({
                    'resource': entry.resource,
                    'action': entry.action,
                    'timestamp': entry.timestamp.isoformat() if entry.timestamp else None,
                    'subsystem': entry.subsystem
                })
            
            return similar_fixes
    
    async def get_insights(self) -> Dict[str, Any]:
        """Get DL insights"""
        return {
            'embeddings_cached': len(self.embeddings_cache),
            'running': self.running,
            'model_type': 'code_similarity'
        }


# Global instances
ml_healing = MLHealingEngine()
dl_healing = DLHealingEngine()
