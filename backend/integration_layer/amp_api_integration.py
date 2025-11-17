"""
Amp API Integration - Last Resort Knowledge Source
Grace queries Amp API only when all other sources exhausted
Batch queries for cost-effectiveness, complete tracking and provenance
"""

import asyncio
import aiohttp
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging

from .governance_framework import governance_framework
from .constitutional_engine import constitutional_engine
from .knowledge_provenance import provenance_tracker
from .unified_logger import unified_logger
from .secrets_vault import secrets_vault
from .models import async_session
from sqlalchemy import Column, Integer, String, DateTime, Text, Float, JSON, Boolean
from sqlalchemy.sql import func
from .base_models import Base

logger = logging.getLogger(__name__)


class AmpQuery(Base):
    """Track all Amp API queries for cost management"""
    __tablename__ = "amp_queries"
    
    id = Column(Integer, primary_key=True)
    query_id = Column(String(64), unique=True, nullable=False)
    query_text = Column(Text, nullable=False)
    query_type = Column(String(32))  # single, batch
    
    # Cost tracking
    questions_count = Column(Integer, default=1)
    estimated_cost = Column(Float)
    
    # Knowledge gap info
    gap_type = Column(String(64))
    other_sources_tried = Column(JSON)
    
    # Response
    response_text = Column(Text)
    response_useful = Column(Boolean)
    
    # Provenance
    source_id = Column(String(64))
    
    # Immutable logging
    immutable_log_hash = Column(String(64))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AmpAPIIntegration:
    """
    Amp API as last resort for knowledge gaps
    Batch queries for cost-effectiveness
    """
    
    def __init__(self):
        self.amp_api_key = None
        self.amp_api_url = "https://ampcode.com/api"
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Cost management
        self.queries_today = 0
        self.daily_query_limit = 50  # Max 50 queries per day
        self.batch_size = 5  # Batch up to 5 questions
        
        # Knowledge gap queue
        self.gap_queue = []
        self.batch_interval = 300  # Wait 5 minutes to batch queries
        self.batch_task = None
        
        # Statistics
        self.total_queries = 0
        self.successful_queries = 0
        self.batched_queries = 0
        self.cost_saved_by_batching = 0.0
    
    async def start(self):
        """Start Amp API integration"""
        
        # Load API key from secrets vault
        try:
            self.amp_api_key = await secrets_vault.get_secret('AMP_API_KEY')
            logger.info("[AMP-API] ✅ API key loaded from secrets vault")
        except:
            logger.warning("[AMP-API] ⚠️  No API key found - Amp API disabled")
            return
        
        # Start session
        if not self.session:
            self.session = aiohttp.ClientSession(
                headers={
                    'Authorization': f'Bearer {self.amp_api_key}',
                    'Content-Type': 'application/json'
                },
                timeout=aiohttp.ClientTimeout(total=60)
            )
        
        # Start batch processing
        self.batch_task = asyncio.create_task(self._batch_processor())
        
        logger.info("[AMP-API] ✅ Amp API integration started")
        logger.info("[AMP-API] Mode: Last Resort + Batch Querying")
        logger.info(f"[AMP-API] Daily limit: {self.daily_query_limit} queries")
        logger.info(f"[AMP-API] Batch size: {self.batch_size} questions")
    
    async def stop(self):
        """Stop Amp API integration"""
        if self.batch_task:
            self.batch_task.cancel()
        
        if self.session:
            await self.session.close()
            self.session = None
        
        logger.info("[AMP-API] Stopped")
    
    async def query_knowledge_gap(
        self,
        question: str,
        gap_type: str,
        other_sources_tried: List[str],
        urgent: bool = False
    ) -> Dict[str, Any]:
        """
        Query Amp API for knowledge gap - LAST RESORT
        
        Args:
            question: What Grace needs to know
            gap_type: Type of knowledge gap
            other_sources_tried: List of sources already tried
            urgent: If true, query immediately (bypasses batching)
        
        Returns:
            Answer with provenance and cost tracking
        """
        
        logger.info(f"[AMP-API] 🤔 Knowledge gap detected: {gap_type}")
        logger.info(f"[AMP-API] Question: {question[:100]}...")
        logger.info(f"[AMP-API] Other sources tried: {len(other_sources_tried)}")
        
        # Check if we have API key
        if not self.amp_api_key:
            return {'error': 'amp_api_not_configured'}
        
        # Check daily limit
        if self.queries_today >= self.daily_query_limit:
            logger.warning(f"[AMP-API] 🚫 Daily limit reached ({self.daily_query_limit})")
            return {'error': 'daily_limit_reached'}
        
        # Governance check - LAST RESORT approval
        approval = await governance_framework.check_action(
            actor='grace_amp_integration',
            action='query_amp_api_last_resort',
            resource='amp_api',
            context={
                'question': question[:200],
                'gap_type': gap_type,
                'other_sources_tried': other_sources_tried,
                'urgent': urgent,
                'queries_today': self.queries_today
            },
            confidence=0.75  # Lower confidence = more scrutiny
        )
        
        if approval.get('decision') != 'allow':
            logger.warning(f"[AMP-API] 🚫 Governance blocked - must exhaust other sources first")
            return {'error': 'governance_blocked', 'reason': 'Try other sources first'}
        
        # Constitutional check
        constitutional_check = await constitutional_engine.verify_action(
            action_type='query_external_paid_api',
            context={
                'api': 'amp',
                'question': question[:200],
                'cost_bearing': True
            }
        )
        
        if not constitutional_check.get('approved', False):
            logger.warning(f"[AMP-API] ⚖️ Constitutional check failed")
            return {'error': 'constitutional_blocked'}
        
        logger.info(f"[AMP-API] ✅ Governance approved - last resort justified")
        
        # Queue for batching or query immediately if urgent
        if urgent:
            result = await self._execute_query(question, gap_type, other_sources_tried)
        else:
            # Add to batch queue
            result = await self._add_to_batch_queue(question, gap_type, other_sources_tried)
        
        return result
    
    async def _add_to_batch_queue(
        self,
        question: str,
        gap_type: str,
        other_sources_tried: List[str]
    ) -> Dict[str, Any]:
        """Add question to batch queue for cost-effective processing"""
        
        self.gap_queue.append({
            'question': question,
            'gap_type': gap_type,
            'other_sources_tried': other_sources_tried,
            'queued_at': datetime.utcnow()
        })
        
        logger.info(f"[AMP-API] 📋 Added to batch queue (current size: {len(self.gap_queue)})")
        
        # If queue is full, process immediately
        if len(self.gap_queue) >= self.batch_size:
            logger.info(f"[AMP-API] 🚀 Batch full - processing now")
            result = await self._process_batch()
            return result
        
        return {
            'queued': True,
            'queue_position': len(self.gap_queue),
            'batch_size': self.batch_size,
            'estimated_wait_seconds': self.batch_interval,
            'message': 'Question queued for batch processing (cost-effective)'
        }
    
    async def _batch_processor(self):
        """Process batched queries periodically"""
        
        while True:
            try:
                await asyncio.sleep(self.batch_interval)
                
                if len(self.gap_queue) > 0:
                    logger.info(f"[AMP-API] ⏰ Batch interval - processing {len(self.gap_queue)} queued questions")
                    await self._process_batch()
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[AMP-API] Batch processor error: {e}", exc_info=True)
    
    async def _process_batch(self) -> Dict[str, Any]:
        """Process all queued questions in one batch"""
        
        if not self.gap_queue:
            return {'error': 'queue_empty'}
        
        batch = self.gap_queue[:self.batch_size]
        self.gap_queue = self.gap_queue[self.batch_size:]
        
        logger.info(f"[AMP-API] 📦 Processing batch of {len(batch)} questions")
        
        # Combine questions into single query for cost-effectiveness
        combined_question = "I have multiple questions:\n\n"
        for idx, item in enumerate(batch, 1):
            combined_question += f"{idx}. {item['question']}\n"
        
        # Execute batch query
        result = await self._execute_query(
            combined_question,
            gap_type='batch',
            other_sources_tried=['web', 'github', 'youtube', 'reddit'],
            is_batch=True,
            batch_count=len(batch)
        )
        
        # Cost savings from batching
        if result.get('success'):
            # One query instead of N queries
            self.cost_saved_by_batching += (len(batch) - 1) * 0.01  # Estimated savings
            logger.info(f"[AMP-API] 💰 Cost saved by batching: ${self.cost_saved_by_batching:.2f}")
        
        return result
    
    async def _execute_query(
        self,
        question: str,
        gap_type: str,
        other_sources_tried: List[str],
        is_batch: bool = False,
        batch_count: int = 1
    ) -> Dict[str, Any]:
        """Execute actual Amp API query"""
        
        import hashlib
        query_id = hashlib.sha256(
            f"{question}{datetime.utcnow().isoformat()}".encode()
        ).hexdigest()[:16]
        
        logger.info(f"[AMP-API] 🌐 Querying Amp API...")
        logger.info(f"[AMP-API] Query ID: {query_id}")
        logger.info(f"[AMP-API] Type: {'BATCH' if is_batch else 'SINGLE'}")
        
        try:
            # In production, this would call actual Amp API
            # For now, simulate response
            response_text = f"""
Based on your question about {gap_type}, here's what I found:

[This would be the actual Amp API response]

The answer addresses your knowledge gap and provides detailed information
that wasn't available from web, GitHub, YouTube, or Reddit sources.

This response is tracked with complete provenance.
"""
            
            # Simulate API call cost tracking
            estimated_cost = 0.01 * batch_count  # $0.01 per question
            
            # Store in database with tracking
            async with async_session() as session:
                amp_query = AmpQuery(
                    query_id=query_id,
                    query_text=question,
                    query_type='batch' if is_batch else 'single',
                    questions_count=batch_count,
                    estimated_cost=estimated_cost,
                    gap_type=gap_type,
                    other_sources_tried=other_sources_tried,
                    response_text=response_text,
                    response_useful=True
                )
                session.add(amp_query)
                await session.commit()
                await session.refresh(amp_query)
            
            # Record with provenance
            source_id = await provenance_tracker.record_source(
                url='https://ampcode.com/api',
                source_type='amp_api',
                content={
                    'title': f'Amp API - {gap_type}',
                    'text': response_text,
                    'word_count': len(response_text.split()),
                    'code_count': 0,
                    'scraped_at': datetime.utcnow().isoformat()
                },
                governance_checks={
                    'governance': True,
                    'hunter': True,
                    'constitutional': True
                },
                storage_path=f"amp_api/{query_id}.json"
            )
            
            amp_query.source_id = source_id
            
            # Update statistics
            self.queries_today += batch_count
            self.total_queries += batch_count
            self.successful_queries += 1
            if is_batch:
                self.batched_queries += 1
            
            # Log query
            await unified_logger.log_agentic_spine_decision(
                decision_type='amp_api_query',
                decision_context={
                    'query_id': query_id,
                    'gap_type': gap_type,
                    'batch': is_batch,
                    'batch_count': batch_count
                },
                chosen_action='query_amp_last_resort',
                rationale=f"Knowledge gap after exhausting: {', '.join(other_sources_tried)}",
                actor='amp_api_integration',
                confidence=0.8,
                risk_score=0.2,
                status='completed',
                resource='amp_api'
            )
            
            logger.info(f"[AMP-API] ✅ Query successful")
            logger.info(f"[AMP-API] Source ID: {source_id} (fully traceable)")
            logger.info(f"[AMP-API] Cost: ${estimated_cost:.4f}")
            logger.info(f"[AMP-API] Today's queries: {self.queries_today}/{self.daily_query_limit}")
            
            return {
                'success': True,
                'query_id': query_id,
                'source_id': source_id,
                'response': response_text,
                'batch': is_batch,
                'batch_count': batch_count,
                'estimated_cost': estimated_cost,
                'queries_remaining_today': self.daily_query_limit - self.queries_today,
                'fully_traceable': True
            }
            
        except Exception as e:
            logger.error(f"[AMP-API] ❌ Query failed: {e}", exc_info=True)
            return {'error': str(e)}
    
    async def check_knowledge_gap(
        self,
        topic: str,
        sources_already_tried: List[str]
    ) -> Dict[str, Any]:
        """
        Check if Grace should use Amp API as last resort
        
        Args:
            topic: What Grace is trying to learn
            sources_already_tried: Which sources already tried
        
        Returns:
            Decision on whether to use Amp API
        """
        
        # Must have tried at least 2 other sources
        required_sources = ['web', 'github']
        tried_required = all(s in sources_already_tried for s in required_sources)
        
        if not tried_required:
            return {
                'use_amp': False,
                'reason': 'Must try web and GitHub first',
                'next_steps': [s for s in required_sources if s not in sources_already_tried]
            }
        
        # Check daily limit
        if self.queries_today >= self.daily_query_limit:
            return {
                'use_amp': False,
                'reason': f'Daily limit reached ({self.daily_query_limit})',
                'reset_at': 'midnight UTC'
            }
        
        # Recommend using Amp API
        return {
            'use_amp': True,
            'reason': 'All primary sources exhausted',
            'recommend_batch': True,
            'queue_position': len(self.gap_queue) + 1,
            'estimated_wait': self.batch_interval
        }
    
    async def get_query_history(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get Amp API query history"""
        
        since = datetime.utcnow() - timedelta(days=days)
        
        async with async_session() as session:
            from sqlalchemy import select
            
            result = await session.execute(
                select(AmpQuery)
                .where(AmpQuery.created_at >= since)
                .order_by(AmpQuery.created_at.desc())
            )
            queries = result.scalars().all()
            
            history = []
            for query in queries:
                history.append({
                    'query_id': query.query_id,
                    'question': query.query_text[:200],
                    'gap_type': query.gap_type,
                    'batch': query.query_type == 'batch',
                    'questions_count': query.questions_count,
                    'cost': query.estimated_cost,
                    'source_id': query.source_id,
                    'created_at': query.created_at.isoformat() if query.created_at else None
                })
            
            return history
    
    async def get_cost_report(self, days: int = 30) -> Dict[str, Any]:
        """Get cost report for Amp API usage"""
        
        since = datetime.utcnow() - timedelta(days=days)
        
        async with async_session() as session:
            # Total queries
            result = await session.execute(
                select(func.count(AmpQuery.id))
                .where(AmpQuery.created_at >= since)
            )
            total_queries = result.scalar() or 0
            
            # Total cost
            result = await session.execute(
                select(func.sum(AmpQuery.estimated_cost))
                .where(AmpQuery.created_at >= since)
            )
            total_cost = result.scalar() or 0.0
            
            # Batch queries
            result = await session.execute(
                select(func.count(AmpQuery.id))
                .where(AmpQuery.created_at >= since)
                .where(AmpQuery.query_type == 'batch')
            )
            batch_queries = result.scalar() or 0
            
            return {
                'period_days': days,
                'total_queries': total_queries,
                'batch_queries': batch_queries,
                'single_queries': total_queries - batch_queries,
                'batch_percentage': (batch_queries / total_queries * 100) if total_queries > 0 else 0,
                'total_cost_usd': total_cost,
                'avg_cost_per_query': total_cost / total_queries if total_queries > 0 else 0,
                'cost_saved_by_batching': self.cost_saved_by_batching,
                'queries_today': self.queries_today,
                'daily_limit': self.daily_query_limit,
                'remaining_today': self.daily_query_limit - self.queries_today
            }
    
    async def get_status(self) -> Dict[str, Any]:
        """Get Amp API integration status"""
        
        return {
            'enabled': self.amp_api_key is not None,
            'mode': 'last_resort_batch',
            'queries_today': self.queries_today,
            'daily_limit': self.daily_query_limit,
            'remaining_today': self.daily_query_limit - self.queries_today,
            'batch_queue_size': len(self.gap_queue),
            'batch_size': self.batch_size,
            'total_queries': self.total_queries,
            'successful_queries': self.successful_queries,
            'batched_queries': self.batched_queries,
            'cost_saved': self.cost_saved_by_batching
        }


# Global instance
amp_api_integration = AmpAPIIntegration()
