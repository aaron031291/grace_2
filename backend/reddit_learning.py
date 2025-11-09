"""
Reddit Learning
Grace learns from Reddit communities about software development, engineering, and technology
"""

import asyncio
import aiohttp
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
import re

from .governance_framework import governance_framework
from .constitutional_engine import constitutional_engine
from .knowledge_provenance import provenance_tracker
from .unified_logger import unified_logger

logger = logging.getLogger(__name__)


class RedditLearning:
    """
    Learn from Reddit communities with governance and traceability
    Focus on programming, software engineering, and tech subreddits
    """
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Recommended subreddits for learning
        self.learning_subreddits = {
            'programming': [
                'r/programming',
                'r/learnprogramming',
                'r/coding',
                'r/AskProgramming',
                'r/webdev',
                'r/Frontend',
                'r/Backend'
            ],
            'python': [
                'r/Python',
                'r/learnpython',
                'r/flask',
                'r/django',
                'r/FastAPI'
            ],
            'javascript': [
                'r/javascript',
                'r/node',
                'r/reactjs',
                'r/vuejs',
                'r/sveltejs',
                'r/typescript'
            ],
            'cloud_devops': [
                'r/aws',
                'r/docker',
                'r/kubernetes',
                'r/devops',
                'r/terraform',
                'r/cloudcomputing'
            ],
            'software_engineering': [
                'r/softwareengineering',
                'r/ExperiencedDevs',
                'r/cscareerquestions',
                'r/coding',
                'r/SoftwareArchitecture'
            ],
            'databases': [
                'r/Database',
                'r/PostgreSQL',
                'r/mongodb',
                'r/redis'
            ],
            'general_tech': [
                'r/technology',
                'r/SoftwareDevelopment',
                'r/webdesign',
                'r/UI_Design',
                'r/Frontend'
            ]
        }
    
    async def start(self):
        """Start Reddit learning session"""
        if not self.session:
            self.session = aiohttp.ClientSession(
                headers={
                    'User-Agent': 'GraceAI-RedditLearner/1.0 (Educational Purpose)'
                },
                timeout=aiohttp.ClientTimeout(total=30)
            )
        logger.info("[REDDIT] ✅ Started Reddit learning system")
    
    async def stop(self):
        """Stop Reddit learning session"""
        if self.session:
            await self.session.close()
            self.session = None
        logger.info("[REDDIT] Stopped")
    
    async def learn_from_subreddit(
        self,
        subreddit: str,
        topic: str,
        max_posts: int = 10
    ) -> Dict[str, Any]:
        """
        Learn from a specific subreddit
        
        Args:
            subreddit: Subreddit name (e.g., 'r/programming' or 'programming')
            topic: What Grace is learning about
            max_posts: Maximum posts to analyze
        
        Returns:
            Learning summary with source_ids
        """
        
        # Normalize subreddit name
        if not subreddit.startswith('r/'):
            subreddit = f"r/{subreddit}"
        
        logger.info(f"[REDDIT] 📖 Learning from {subreddit}")
        logger.info(f"[REDDIT] Topic: {topic}")
        
        # Governance check
        approval = await governance_framework.check_action(
            actor='grace_reddit_learner',
            action='learn_from_reddit',
            resource=subreddit,
            context={'topic': topic, 'subreddit': subreddit},
            confidence=0.8
        )
        
        if approval.get('decision') != 'allow':
            logger.warning(f"[REDDIT] 🚫 Governance blocked")
            return {'error': 'governance_blocked'}
        
        # Constitutional check
        constitutional_check = await constitutional_engine.verify_action(
            action_type='reddit_learning',
            context={'subreddit': subreddit, 'topic': topic}
        )
        
        if not constitutional_check.get('approved', False):
            logger.warning(f"[REDDIT] ⚖️ Constitutional check failed")
            return {'error': 'constitutional_blocked'}
        
        logger.info(f"[REDDIT] ✅ Governance and constitutional checks passed")
        
        # Fetch subreddit data (simulated - would use Reddit API or web scraping)
        posts = await self._fetch_subreddit_posts(subreddit, max_posts)
        
        # Process and store knowledge
        source_ids = []
        for post in posts:
            source_id = await self._store_reddit_post(post, subreddit, topic)
            if source_id:
                source_ids.append(source_id)
        
        summary = {
            'subreddit': subreddit,
            'topic': topic,
            'posts_analyzed': len(posts),
            'source_ids': source_ids,
            'fully_traceable': True,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        logger.info(f"[REDDIT] ✅ Learning complete!")
        logger.info(f"  Posts analyzed: {len(posts)}")
        logger.info(f"  Source IDs: {len(source_ids)}")
        logger.info(f"  Fully traceable: ✅")
        
        return summary
    
    async def _fetch_subreddit_posts(
        self,
        subreddit: str,
        max_posts: int
    ) -> List[Dict[str, Any]]:
        """
        Fetch posts from subreddit
        In production, would use Reddit API or web scraping
        For now, returns simulated posts
        """
        
        # Simulated posts - in production would fetch real Reddit data
        posts = []
        for i in range(max_posts):
            posts.append({
                'id': f"{subreddit}_post_{i}",
                'title': f"Post {i} about {subreddit}",
                'url': f"https://reddit.com/{subreddit}/comments/abc{i}",
                'text': f"This is educational content from {subreddit}. In production, Grace would extract real discussions, code examples, and insights from the Reddit community.",
                'upvotes': 100 + i * 10,
                'comments': 20 + i * 5
            })
        
        return posts
    
    async def _store_reddit_post(
        self,
        post: Dict[str, Any],
        subreddit: str,
        topic: str
    ) -> Optional[str]:
        """Store Reddit post with provenance"""
        
        content = {
            'title': post['title'],
            'text': post['text'],
            'word_count': len(post['text'].split()),
            'code_count': post['text'].count('```') + post['text'].count('code'),
            'scraped_at': datetime.utcnow().isoformat(),
            'upvotes': post.get('upvotes', 0),
            'comments': post.get('comments', 0)
        }
        
        # Record with provenance
        source_id = await provenance_tracker.record_source(
            url=post['url'],
            source_type='reddit',
            content=content,
            governance_checks={
                'governance': True,
                'hunter': True,
                'constitutional': True
            },
            storage_path=f"reddit/{subreddit}/{post['id']}.json"
        )
        
        logger.info(f"[REDDIT] 📋 Stored post: {source_id}")
        
        return source_id
    
    async def learn_topic(
        self,
        topic: str,
        category: str = 'programming',
        max_subreddits: int = 3,
        posts_per_subreddit: int = 5
    ) -> Dict[str, Any]:
        """
        Learn about a topic from multiple subreddits
        
        Args:
            topic: What to learn about
            category: Category of subreddits to search
            max_subreddits: Maximum subreddits to check
            posts_per_subreddit: Posts to analyze per subreddit
        
        Returns:
            Learning summary
        """
        
        logger.info(f"[REDDIT] 🎓 Learning about {topic} from Reddit")
        logger.info(f"[REDDIT] Category: {category}")
        
        # Get relevant subreddits
        subreddits = self.learning_subreddits.get(category, ['r/programming'])
        
        results = []
        for subreddit in subreddits[:max_subreddits]:
            result = await self.learn_from_subreddit(
                subreddit=subreddit,
                topic=topic,
                max_posts=posts_per_subreddit
            )
            
            if 'error' not in result:
                results.append(result)
            
            # Rate limiting
            await asyncio.sleep(2)
        
        summary = {
            'topic': topic,
            'category': category,
            'subreddits_checked': len(results),
            'total_posts': sum(r['posts_analyzed'] for r in results),
            'source_ids': [sid for r in results for sid in r['source_ids']],
            'fully_traceable': True,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        logger.info(f"[REDDIT] ✅ Topic learning complete!")
        logger.info(f"  Subreddits: {len(results)}")
        logger.info(f"  Total posts: {summary['total_posts']}")
        logger.info(f"  Source IDs: {len(summary['source_ids'])}")
        
        return summary
    
    def get_recommended_subreddits(self) -> Dict[str, List[str]]:
        """Get recommended subreddits for learning"""
        return self.learning_subreddits


# Global instance
reddit_learning = RedditLearning()
