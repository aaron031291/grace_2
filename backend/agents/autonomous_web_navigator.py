"""
Autonomous Web Navigator Agent
Teaches Grace when and how to search the web autonomously
"""

import logging
import re
from typing import Dict, Any, List, Optional
from datetime import datetime
import yaml
from pathlib import Path

logger = logging.getLogger(__name__)


class AutonomousWebNavigator:
    """
    Autonomous agent that decides when Grace should search the web
    and executes web learning strategies based on playbook
    """
    
    def __init__(self):
        self.playbook = None
        self.searches_triggered = 0
        self.knowledge_gaps_filled = 0
        self.last_search_time = None
        self._initialized = False
        
    async def initialize(self):
        """Load web navigation playbook"""
        if self._initialized:
            return
            
        try:
            playbook_path = Path(__file__).parent.parent.parent / "playbooks" / "web_navigation_playbook.yaml"
            if playbook_path.exists():
                with open(playbook_path, 'r', encoding='utf-8') as f:
                    # Load all documents and merge (YAML file has multiple --- separators)
                    docs = list(yaml.safe_load_all(f))
                    self.playbook = docs[0] if docs else {}
                logger.info("[WEB-NAVIGATOR] Loaded web navigation playbook")
            else:
                logger.warning(f"[WEB-NAVIGATOR] Playbook not found: {playbook_path}")
        except Exception as e:
            logger.error(f"[WEB-NAVIGATOR] Failed to load playbook: {e}")
        
        self._initialized = True
    
    async def should_search_web(
        self,
        context: Dict[str, Any]
    ) -> tuple[bool, str, Optional[str]]:
        """
        Decide if Grace should search the web
        
        Args:
            context: {
                'query': user query or task,
                'confidence': Grace's confidence in answer (0-1),
                'knowledge_match': knowledge base match score (0-1),
                'error_occurred': bool,
                'task_type': 'question' | 'error' | 'research' | 'general'
            }
        
        Returns:
            (should_search, reason, strategy)
        """
        if not self._initialized:
            await self.initialize()
        
        query = context.get('query', '')
        confidence = context.get('confidence', 1.0)
        knowledge_match = context.get('knowledge_match', 1.0)
        error_occurred = context.get('error_occurred', False)
        task_type = context.get('task_type', 'general')
        
        # Check triggers from playbook
        if not self.playbook:
            return False, "Playbook not loaded", None
        
        triggers = self.playbook.get('triggers', [])
        
        # Trigger 1: Explicit research request
        research_patterns = [
            r'(?i)(research|look up|find out|learn about|search for)',
            r'(?i)(what is|what are|how does|how do)',
            r'(?i)(tell me about|explain|describe)'
        ]
        
        for pattern in research_patterns:
            if re.search(pattern, query):
                return True, "User requested research/information", "basic_search"
        
        # Trigger 2: Knowledge gap detected
        if confidence < 0.6 or knowledge_match < 0.3:
            return True, f"Knowledge gap (confidence: {confidence}, match: {knowledge_match})", "topic_learning"
        
        # Trigger 3: Error occurred
        if error_occurred:
            return True, "Error needs solution", "solution_search"
        
        # Trigger 4: New technology mentioned
        new_tech_pattern = r'(?i)(new|latest|recent|2025|2024).*(?:framework|library|tool|technology|version)'
        if re.search(new_tech_pattern, query):
            return True, "New technology detected", "explore_domain"
        
        # No triggers matched
        return False, "No trigger conditions met", None
    
    async def execute_search_strategy(
        self,
        strategy_name: str,
        topic: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Execute a web search strategy from playbook
        
        Args:
            strategy_name: 'basic_search' | 'topic_learning' | 'domain_exploration' | etc.
            topic: What to search for
            context: Additional context
        
        Returns:
            Search results and learned knowledge
        """
        # from backend.services.google_search_service import google_search_service
        from backend.services.closed_loop_learning import closed_loop_learning
        
        self.searches_triggered += 1
        self.last_search_time = datetime.utcnow()
        
        result = {
            'strategy': strategy_name,
            'topic': topic,
            'timestamp': datetime.utcnow().isoformat(),
            'success': False,
            'error': 'Web navigation disabled per user request.'
        }
        
        logger.info(f"[WEB-NAVIGATOR] Search strategy '{strategy_name}' triggered but disabled.")
        return result

        # try:
        #     if strategy_name == 'basic_search':
        #         # Simple search
        #         search_results = await google_search_service.search(
        #             query=topic,
        #             num_results=5
        #         )
        #         
        #         result['results'] = search_results
        #         result['count'] = len(search_results)
        #         result['success'] = len(search_results) > 0
        #         
        #         # Save knowledge
        #         if search_results:
        #             await self._save_search_knowledge(topic, search_results, strategy_name)
        #             self.knowledge_gaps_filled += 1
            
        #     elif strategy_name == 'topic_learning':
        #         # Deep learning on topic
        #         search_results = await google_search_service.search_and_extract(
        #             query=topic,
        #             num_results=10
        #         )
        #         
        #         result['results'] = search_results.get('results', [])
        #         result['count'] = len(result['results'])
        #         result['success'] = len(result['results']) > 0
        #         
        #         # Capture as learning outcome
        #         if result['results']:
        #             await closed_loop_learning.capture_outcome(
        #                 execution_id=f"web-nav-{datetime.utcnow().timestamp()}",
        #                 task_description=f"Learn about: {topic}",
        #                 approach_taken="Autonomous web navigation - topic learning",
        #                 outcome_type="success",
        #                 outcome_narrative=f"Learned about {topic} from {len(result['results'])} sources",
        #                 metrics={'sources': len(result['results'])},
        #                 learning_points=[r.get('snippet', '')[:100] for r in result['results'][:3]]
        #             )
        #             self.knowledge_gaps_filled += 1
        #     
        #     elif strategy_name == 'solution_search':
        #         # Search for error solutions
        #         # Format query for error searches
        #         error_query = f"{topic} solution fix"
        #         search_results = await google_search_service.search(
        #             query=error_query,
        #             num_results=10,
        #             min_trust_score=0.8  # Higher trust for solutions
        #         )
        #         
        #         # Filter for high-quality sources
        #         filtered = [r for r in search_results if r.get('trust_score', 0) >= 0.8]
        #         
        #         result['results'] = filtered
        #         result['count'] = len(filtered)
        #         result['success'] = len(filtered) > 0
        #         
        #         if filtered:
        #             await self._save_search_knowledge(topic, filtered, strategy_name)
        #             self.knowledge_gaps_filled += 1
        #     
        #     elif strategy_name == 'explore_domain':
        #         # Domain exploration
        #         # Extract domain from topic
        #         domain = topic.split()[0] if ' ' in topic else topic
        #         
        #         exploration_queries = [
        #             f"{domain} fundamentals",
        #             f"{domain} best practices",
        #             f"{domain} examples",
        #             f"latest {domain} trends"
        #         ]
        #         
        #         all_results = []
        #         for query in exploration_queries[:3]:  # Limit to 3 queries
        #             try:
        #                 search_results = await google_search_service.search(query, num_results=3)
        #                 all_results.extend(search_results)
        #             except Exception as e:
        #                 logger.warning(f"[WEB-NAVIGATOR] Query failed: {query} - {e}")
        #         
        #         result['results'] = all_results
        #         result['count'] = len(all_results)
        #         result['success'] = len(all_results) > 0
        #         result['exploration_queries'] = exploration_queries[:3]
        #         
        #         if all_results:
        #             await self._save_search_knowledge(topic, all_results, strategy_name)
        #             self.knowledge_gaps_filled += 1
        #     
        #     else:
        #         result['error'] = f"Unknown strategy: {strategy_name}"
        #         logger.warning(f"[WEB-NAVIGATOR] Unknown strategy: {strategy_name}")
        # 
        # except Exception as e:
        #     result['error'] = str(e)
        #     result['success'] = False
        #     logger.error(f"[WEB-NAVIGATOR] Strategy execution failed: {e}")
        
        return result
    
    async def _save_search_knowledge(
        self,
        topic: str,
        results: List[Dict[str, Any]],
        strategy: str
    ):
        """Save search results to knowledge base"""
        try:
            from backend.services.closed_loop_learning import closed_loop_learning
            
            # Extract key learnings
            learning_points = []
            for result in results[:5]:
                if result.get('snippet'):
                    learning_points.append(result['snippet'][:200])
            
            # Capture outcome
            await closed_loop_learning.capture_outcome(
                execution_id=f"auto-search-{datetime.utcnow().timestamp()}",
                task_description=f"Autonomous search: {topic}",
                approach_taken=f"Web navigation strategy: {strategy}",
                outcome_type="success",
                outcome_narrative=f"Searched web for '{topic}', found {len(results)} sources",
                metrics={
                    'sources_found': len(results),
                    'avg_trust_score': sum(r.get('trust_score', 0) for r in results) / len(results) if results else 0,
                    'strategy': strategy
                },
                learning_points=learning_points
            )
            
            logger.info(f"[WEB-NAVIGATOR] Saved knowledge from search: {topic}")
        
        except Exception as e:
            logger.warning(f"[WEB-NAVIGATOR] Failed to save knowledge: {e}")
    
    async def auto_navigate(
        self,
        user_query: str,
        grace_confidence: float = 0.5,
        knowledge_match: float = 0.5
    ) -> Optional[Dict[str, Any]]:
        """
        Autonomous decision to search web and execute
        
        This is the main method that Grace calls when processing queries
        
        Args:
            user_query: The user's question or request
            grace_confidence: Grace's confidence she can answer (0-1)
            knowledge_match: How well existing knowledge matches (0-1)
        
        Returns:
            Search results if web search was triggered, None otherwise
        """
        context = {
            'query': user_query,
            'confidence': grace_confidence,
            'knowledge_match': knowledge_match,
            'error_occurred': 'error' in user_query.lower() or 'exception' in user_query.lower(),
            'task_type': 'question'
        }
        
        # Decide if should search
        should_search, reason, strategy = await self.should_search_web(context)
        
        if not should_search:
            logger.debug(f"[WEB-NAVIGATOR] No search needed: {reason}")
            return None
        
        logger.info(f"[WEB-NAVIGATOR] Triggering search: {reason}")
        logger.info(f"[WEB-NAVIGATOR] Strategy: {strategy}")
        
        # Execute search strategy
        result = await self.execute_search_strategy(
            strategy_name=strategy,
            topic=user_query,
            context=context
        )
        
        return result
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get web navigation metrics"""
        return {
            'searches_triggered_automatically': self.searches_triggered,
            'knowledge_gaps_filled': self.knowledge_gaps_filled,
            'last_search': self.last_search_time.isoformat() if self.last_search_time else None,
            'playbook_loaded': self.playbook is not None,
            'initialized': self._initialized
        }


# Global instance
autonomous_web_navigator = AutonomousWebNavigator()
