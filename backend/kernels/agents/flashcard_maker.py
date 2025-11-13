"""
Flashcard Maker Agent
Creates summaries/insights for study workflows
"""

from typing import Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class FlashcardMaker:
    """
    Generates flashcards and study insights from documents.
    Logs to memory_insights for Grace's recall.
    """
    
    def __init__(self, agent_id: str, task_data: Dict, registry=None, kernel=None):
        self.agent_id = agent_id
        self.task_data = task_data
        self.registry = registry
        self.kernel = kernel
        
        self.file_path = task_data.get('path')
        self.domain = task_data.get('domain', 'general')
    
    async def execute(self) -> Dict[str, Any]:
        """
        Generate flashcards:
        1. Extract key concepts from content
        2. Generate Q&A pairs
        3. Create summary insights
        4. Log to memory_insights
        """
        try:
            logger.info(f"Flashcard Maker {self.agent_id} processing: {self.file_path}")
            
            # Step 1: Extract content
            content = await self._extract_content()
            
            # Step 2: Generate flashcards
            flashcards = await self._generate_flashcards(content)
            
            # Step 3: Create summary
            summary = await self._create_summary(content)
            
            # Step 4: Log insights
            await self._log_insights(flashcards, summary)
            
            return {
                'status': 'success',
                'agent_id': self.agent_id,
                'file_path': self.file_path,
                'flashcards_generated': len(flashcards),
                'summary_created': bool(summary)
            }
            
        except Exception as e:
            logger.error(f"Flashcard Maker {self.agent_id} failed: {e}")
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    async def _extract_content(self) -> str:
        """Extract text content from file"""
        from pathlib import Path
        
        try:
            file_path = Path(self.file_path)
            if file_path.exists() and file_path.suffix in ['.txt', '.md']:
                return file_path.read_text(encoding='utf-8', errors='ignore')
        except Exception as e:
            logger.warning(f"Could not extract content: {e}")
        
        return ""
    
    async def _generate_flashcards(self, content: str) -> list:
        """Generate Q&A flashcards from content"""
        # Placeholder: in production, use LLM to extract key Q&A
        
        if not content:
            return []
        
        # Simple heuristic: extract sentences with question marks
        sentences = content.split('.')
        flashcards = []
        
        for i, sentence in enumerate(sentences[:10]):  # Limit to 10
            if len(sentence.strip()) > 20:
                flashcards.append({
                    'id': i,
                    'question': f"What does this passage discuss? {sentence[:100]}...",
                    'answer': sentence.strip(),
                    'domain': self.domain,
                    'source': self.file_path
                })
        
        logger.info(f"Generated {len(flashcards)} flashcards")
        return flashcards
    
    async def _create_summary(self, content: str) -> str:
        """Create a summary of the content"""
        if not content:
            return ""
        
        # Placeholder: extract first paragraph
        paragraphs = content.split('\n\n')
        summary = paragraphs[0] if paragraphs else content[:500]
        
        return summary.strip()
    
    async def _log_insights(self, flashcards: list, summary: str):
        """Log flashcards and summary to memory_insights"""
        if not self.registry:
            return
        
        try:
            # Log summary
            if summary:
                self.registry.insert_row('memory_insights', {
                    'insight_type': 'summary',
                    'source': self.agent_id,
                    'content': summary,
                    'metadata': {
                        'file_path': self.file_path,
                        'domain': self.domain
                    },
                    'created_at': datetime.utcnow().isoformat()
                })
            
            # Log flashcards
            for card in flashcards:
                self.registry.insert_row('memory_insights', {
                    'insight_type': 'flashcard',
                    'source': self.agent_id,
                    'content': card['question'],
                    'metadata': {
                        'answer': card['answer'],
                        'file_path': self.file_path,
                        'domain': self.domain,
                        'flashcard_id': card['id']
                    },
                    'created_at': datetime.utcnow().isoformat()
                })
            
            logger.info(f"Logged {len(flashcards)} flashcards to memory_insights")
            
        except Exception as e:
            logger.error(f"Failed to log insights: {e}")
    
    async def stop(self):
        """Stop the agent"""
        logger.info(f"Stopping Flashcard Maker {self.agent_id}")
