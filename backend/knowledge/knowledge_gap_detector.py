"""
Knowledge Gap Detector
Detects when Grace has exhausted all free sources and needs Amp API as last resort
Tracks what sources were tried and makes cost-effective decisions
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from .safe_web_scraper import safe_web_scraper
from .github_knowledge_miner import github_miner
from .youtube_learning import youtube_learning
from .reddit_learning import reddit_learning
from .amp_api_integration import amp_api_integration
from .unified_logger import unified_logger

logger = logging.getLogger(__name__)


class KnowledgeGapDetector:
    """
    Detects knowledge gaps and orchestrates last-resort Amp API usage
    Ensures all free sources exhausted first (cost-effective)
    """
    
    def __init__(self):
        self.gaps_detected = 0
        self.gaps_resolved_free = 0
        self.gaps_resolved_amp = 0
        
        # Required sources to try before Amp API
        self.required_sources = [
            'web',
            'github',
            'youtube',
            'reddit'
        ]
    
    async def learn_with_fallback(
        self,
        topic: str,
        category: str = 'programming',
        urgent: bool = False
    ) -> Dict[str, Any]:
        """
        Try to learn about topic with automatic fallback to Amp API
        
        Process:
        1. Try web scraping
        2. Try GitHub
        3. Try YouTube
        4. Try Reddit
        5. If all fail → Batch query Amp API (last resort)
        
        Args:
            topic: What to learn
            category: Learning category
            urgent: If true, skips batching for Amp queries
        
        Returns:
            Learning report with sources used
        """
        
        self.gaps_detected += 1
        
        logger.info(f"[GAP-DETECTOR] 🎯 Learning: {topic}")
        logger.info(f"[GAP-DETECTOR] Strategy: Try free sources → Amp API if needed")
        
        sources_tried = []
        sources_succeeded = []
        sources_failed = []
        
        # PHASE 1: Try Web Scraping
        logger.info(f"[GAP-DETECTOR] 📚 Phase 1: Trying web sources...")
        try:
            web_result = await safe_web_scraper.search_and_learn(
                query=topic,
                topic=topic,
                max_results=3
            )
            sources_tried.append('web')
            
            if web_result.get('scraped', 0) > 0:
                sources_succeeded.append('web')
                logger.info(f"[GAP-DETECTOR] ✅ Web: Found {web_result['scraped']} sources")
                
                # Success! No need for Amp API
                self.gaps_resolved_free += 1
                return self._create_report(topic, sources_tried, sources_succeeded, 'web')
            else:
                sources_failed.append('web')
                logger.warning(f"[GAP-DETECTOR] ❌ Web: No sources found")
        except Exception as e:
            sources_tried.append('web')
            sources_failed.append('web')
            logger.warning(f"[GAP-DETECTOR] ❌ Web failed: {e}")
        
        # PHASE 2: Try GitHub
        logger.info(f"[GAP-DETECTOR] 📚 Phase 2: Trying GitHub...")
        try:
            github_result = await github_miner.learn_from_trending(
                language=topic,
                max_repos=2
            )
            sources_tried.append('github')
            
            if github_result.get('repos_mined', 0) > 0:
                sources_succeeded.append('github')
                logger.info(f"[GAP-DETECTOR] ✅ GitHub: Mined {github_result['repos_mined']} repos")
                
                self.gaps_resolved_free += 1
                return self._create_report(topic, sources_tried, sources_succeeded, 'github')
            else:
                sources_failed.append('github')
                logger.warning(f"[GAP-DETECTOR] ❌ GitHub: No repos found")
        except Exception as e:
            sources_tried.append('github')
            sources_failed.append('github')
            logger.warning(f"[GAP-DETECTOR] ❌ GitHub failed: {e}")
        
        # PHASE 3: Try YouTube
        logger.info(f"[GAP-DETECTOR] 📚 Phase 3: Trying YouTube...")
        try:
            youtube_result = await youtube_learning.learn_topic(
                topic=topic,
                category=category,
                max_videos=3
            )
            sources_tried.append('youtube')
            
            if youtube_result.get('videos_learned', 0) > 0:
                sources_succeeded.append('youtube')
                logger.info(f"[GAP-DETECTOR] ✅ YouTube: Found {youtube_result['videos_learned']} videos")
                
                self.gaps_resolved_free += 1
                return self._create_report(topic, sources_tried, sources_succeeded, 'youtube')
            else:
                sources_failed.append('youtube')
                logger.warning(f"[GAP-DETECTOR] ❌ YouTube: No videos found")
        except Exception as e:
            sources_tried.append('youtube')
            sources_failed.append('youtube')
            logger.warning(f"[GAP-DETECTOR] ❌ YouTube failed: {e}")
        
        # PHASE 4: Try Reddit
        logger.info(f"[GAP-DETECTOR] 📚 Phase 4: Trying Reddit...")
        try:
            reddit_result = await reddit_learning.learn_topic(
                topic=topic,
                category=category,
                max_subreddits=2,
                posts_per_subreddit=5
            )
            sources_tried.append('reddit')
            
            if reddit_result.get('subreddits_checked', 0) > 0:
                sources_succeeded.append('reddit')
                logger.info(f"[GAP-DETECTOR] ✅ Reddit: Checked {reddit_result['subreddits_checked']} subreddits")
                
                self.gaps_resolved_free += 1
                return self._create_report(topic, sources_tried, sources_succeeded, 'reddit')
            else:
                sources_failed.append('reddit')
                logger.warning(f"[GAP-DETECTOR] ❌ Reddit: No discussions found")
        except Exception as e:
            sources_tried.append('reddit')
            sources_failed.append('reddit')
            logger.warning(f"[GAP-DETECTOR] ❌ Reddit failed: {e}")
        
        # PHASE 5: ALL FREE SOURCES EXHAUSTED - Use Amp API (Last Resort)
        logger.warning(f"[GAP-DETECTOR] ⚠️  All free sources exhausted!")
        logger.info(f"[GAP-DETECTOR] 💡 Falling back to Amp API (last resort)")
        
        # Check if Amp API is viable
        gap_check = await amp_api_integration.check_knowledge_gap(
            topic=topic,
            sources_already_tried=sources_tried
        )
        
        if not gap_check.get('use_amp', False):
            logger.warning(f"[GAP-DETECTOR] 🚫 Cannot use Amp API: {gap_check.get('reason')}")
            return self._create_report(topic, sources_tried, sources_succeeded, None, gap_check)
        
        # Query Amp API
        logger.info(f"[AMP-API] 🌐 Using Amp API as LAST RESORT")
        
        amp_result = await amp_api_integration.query_knowledge_gap(
            question=f"I need to learn about {topic}. I've tried web docs, GitHub, YouTube, and Reddit but found no good sources. Can you provide comprehensive information about {topic}?",
            gap_type=topic,
            other_sources_tried=sources_tried,
            urgent=urgent
        )
        
        sources_tried.append('amp_api')
        
        if amp_result.get('success') or amp_result.get('queued'):
            sources_succeeded.append('amp_api')
            self.gaps_resolved_amp += 1
            logger.info(f"[GAP-DETECTOR] ✅ Gap resolved via Amp API")
            
            return self._create_report(topic, sources_tried, sources_succeeded, 'amp_api', amp_result)
        else:
            sources_failed.append('amp_api')
            logger.error(f"[GAP-DETECTOR] ❌ Even Amp API failed!")
            
            return self._create_report(topic, sources_tried, sources_succeeded, None)
    
    def _create_report(
        self,
        topic: str,
        sources_tried: List[str],
        sources_succeeded: List[str],
        final_source: Optional[str],
        additional_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create learning report"""
        
        return {
            'topic': topic,
            'gap_detected': True,
            'sources_tried': sources_tried,
            'sources_succeeded': sources_succeeded,
            'sources_failed': [s for s in sources_tried if s not in sources_succeeded],
            'final_source': final_source,
            'free_sources_exhausted': final_source == 'amp_api',
            'amp_api_used': final_source == 'amp_api',
            'resolved': final_source is not None,
            'cost_incurred': final_source == 'amp_api',
            'additional_info': additional_info,
            'timestamp': datetime.utcnow().isoformat(),
            'statistics': {
                'total_gaps_detected': self.gaps_detected,
                'resolved_free': self.gaps_resolved_free,
                'resolved_amp': self.gaps_resolved_amp,
                'free_source_rate': (self.gaps_resolved_free / self.gaps_detected * 100) if self.gaps_detected > 0 else 0
            }
        }
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get knowledge gap statistics"""
        
        return {
            'gaps_detected': self.gaps_detected,
            'resolved_with_free_sources': self.gaps_resolved_free,
            'resolved_with_amp_api': self.gaps_resolved_amp,
            'free_source_success_rate': (self.gaps_resolved_free / self.gaps_detected * 100) if self.gaps_detected > 0 else 0,
            'amp_usage_rate': (self.gaps_resolved_amp / self.gaps_detected * 100) if self.gaps_detected > 0 else 0
        }


# Global instance
knowledge_gap_detector = KnowledgeGapDetector()
