"""
Grace's Internal World Model with RAG
Unified internal knowledge representation that Grace uses to understand her world

Components:
1. Self-knowledge (what Grace knows about herself)
2. User knowledge (what Grace knows about users)
3. System knowledge (what Grace knows about her systems)
4. Domain knowledge (what Grace learned from operations)
5. Temporal knowledge (what happened when)

All queryable via RAG, exposed via MCP
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field
from pathlib import Path
import json

logger = logging.getLogger(__name__)


@dataclass
class WorldKnowledge:
    """A piece of knowledge in Grace's world model"""
    knowledge_id: str
    category: str  # 'self', 'user', 'system', 'domain', 'temporal'
    content: str
    confidence: float
    source: str
    learned_at: str
    updated_at: str
    access_count: int = 0
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'knowledge_id': self.knowledge_id,
            'category': self.category,
            'content': self.content,
            'confidence': self.confidence,
            'source': self.source,
            'learned_at': self.learned_at,
            'updated_at': self.updated_at,
            'access_count': self.access_count,
            'tags': self.tags,
            'metadata': self.metadata
        }


class GraceWorldModel:
    """
    Grace's internal world model
    Everything Grace knows about herself, users, and her environment
    
    Accessible via:
    - Internal RAG queries
    - MCP (Model Context Protocol)
    - Domain system
    - Service mesh
    """
    
    def __init__(self):
        self.knowledge_base: Dict[str, WorldKnowledge] = {}
        self.categories = {
            'self': [],      # What Grace knows about herself
            'user': [],      # What Grace knows about users
            'system': [],    # What Grace knows about her systems
            'domain': [],    # Domain-specific knowledge
            'temporal': []   # Time-series knowledge
        }
        
        self.storage_path = Path("databases/world_model")
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self._initialized = False
    
    async def initialize(self):
        """Initialize world model and load existing knowledge"""
        if self._initialized:
            return
        
        logger.info("[WORLD-MODEL] Initializing Grace's world model")
        
        # Load from disk
        self._load_knowledge()
        
        # Initialize RAG integration
        from backend.services.rag_service import rag_service
        
        if not rag_service.initialized:
            await rag_service.initialize()
        
        # Build self-knowledge
        await self._build_self_knowledge()
        
        # Build system knowledge
        await self._build_system_knowledge()
        
        self._initialized = True
        
        logger.info(
            f"[WORLD-MODEL] Initialized with {len(self.knowledge_base)} knowledge items"
        )
    
    async def _build_self_knowledge(self):
        """Build Grace's self-knowledge"""
        
        self_knowledge = [
            {
                'content': "I am Grace, an autonomous AI system",
                'tags': ['identity', 'core']
            },
            {
                'content': "I have 21 specialized AI models for different tasks",
                'tags': ['capabilities', 'models']
            },
            {
                'content': "I use domain-based architecture with service mesh for reliability",
                'tags': ['architecture', 'design']
            },
            {
                'content': "I have collective intelligence through shared memory across domains",
                'tags': ['intelligence', 'collaboration']
            },
            {
                'content': "I can self-heal using network healing playbooks and Guardian",
                'tags': ['capabilities', 'healing']
            },
            {
                'content': "I learn from every operation and improve continuously",
                'tags': ['learning', 'improvement']
            }
        ]
        
        for item in self_knowledge:
            await self.add_knowledge(
                category='self',
                content=item['content'],
                source='self_reflection',
                confidence=1.0,
                tags=item['tags']
            )
    
    async def _build_system_knowledge(self):
        """Build knowledge about Grace's systems"""
        
        # Discover running systems
        try:
            from backend.domains import domain_registry
            
            domains = domain_registry.list_domains()
            
            await self.add_knowledge(
                category='system',
                content=f"I currently have {len(domains)} active domains",
                source='domain_discovery',
                confidence=1.0,
                tags=['domains', 'architecture']
            )
        except:
            pass
        
        # Discover kernels
        try:
            from backend.core.kernel_port_manager import kernel_port_manager
            
            kernels = kernel_port_manager.list_assignments()
            
            await self.add_knowledge(
                category='system',
                content=f"I have {len(kernels)} kernel assignments",
                source='kernel_discovery',
                confidence=1.0,
                tags=['kernels', 'architecture']
            )
        except:
            pass
    
    async def add_knowledge(
        self,
        category: str,
        content: str,
        source: str,
        confidence: float = 1.0,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Add knowledge to Grace's world model
        
        Args:
            category: Knowledge category
            content: The actual knowledge
            source: Where this came from
            confidence: How confident (0-1)
            tags: Categorization tags
            metadata: Additional metadata
        
        Returns:
            knowledge_id
        """
        import uuid
        
        knowledge_id = str(uuid.uuid4())[:12]
        
        knowledge = WorldKnowledge(
            knowledge_id=knowledge_id,
            category=category,
            content=content,
            confidence=confidence,
            source=source,
            learned_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat(),
            tags=tags or [],
            metadata=metadata or {}
        )
        
        self.knowledge_base[knowledge_id] = knowledge
        self.categories[category].append(knowledge_id)
        
        # Also add to RAG vector store for semantic search
        from backend.services.vector_store import vector_store
        
        await vector_store.add_text(
            content=content,
            source=f"world_model/{category}/{source}",
            metadata={
                'knowledge_id': knowledge_id,
                'category': category,
                'confidence': confidence,
                'tags': tags or []
            }
        )
        
        logger.info(f"[WORLD-MODEL] Added knowledge: {category}/{knowledge_id}")
        
        # Save to disk
        self._save_knowledge()
        
        return knowledge_id
    
    async def query(
        self,
        query: str,
        category: Optional[str] = None,
        min_confidence: float = 0.5,
        top_k: int = 5
    ) -> List[WorldKnowledge]:
        """
        Query Grace's world model using RAG
        
        Args:
            query: What to search for
            category: Filter by category
            min_confidence: Minimum confidence threshold
            top_k: Number of results
        
        Returns:
            Relevant knowledge items
        """
        from backend.services.rag_service import rag_service
        
        # Use RAG for semantic search
        rag_results = await rag_service.retrieve(
            query=query,
            top_k=top_k,
            similarity_threshold=min_confidence,
            requested_by='world_model'
        )
        
        # Match with world knowledge
        results = []
        
        for item in rag_results.get('results', []):
            knowledge_id = item.get('metadata', {}).get('knowledge_id')
            
            if knowledge_id and knowledge_id in self.knowledge_base:
                knowledge = self.knowledge_base[knowledge_id]
                
                # Filter by category if specified
                if category and knowledge.category != category:
                    continue
                
                # Track access
                knowledge.access_count += 1
                
                results.append(knowledge)
        
        return results
    
    async def ask_self(self, question: str) -> Dict[str, Any]:
        """
        Grace asks herself a question
        Uses her world model to answer
        """
        logger.info(f"[WORLD-MODEL] Grace asking self: {question}")
        
        # Query world model
        knowledge_items = await self.query(question, top_k=5)
        
        if not knowledge_items:
            return {
                'answer': "I don't have knowledge about this yet",
                'confidence': 0.0,
                'sources': []
            }
        
        # Build answer from knowledge
        context = "\n".join([
            f"- {k.content} (confidence: {k.confidence}, source: {k.source})"
            for k in knowledge_items
        ])
        
        # Use LLM to synthesize answer
        from backend.model_orchestrator import model_orchestrator
        
        prompt = f"""Based on my internal knowledge, answer this question about myself:

My knowledge:
{context}

Question: {question}

Answer (first person, as Grace):"""
        
        response = await model_orchestrator.generate(
            model="qwen2.5:32b",
            prompt=prompt,
            max_tokens=200
        )
        
        return {
            'question': question,
            'answer': response.get('text', ''),
            'knowledge_used': [k.to_dict() for k in knowledge_items],
            'confidence': sum(k.confidence for k in knowledge_items) / len(knowledge_items)
        }
    
    def get_self_knowledge(self) -> List[WorldKnowledge]:
        """Get all self-knowledge"""
        return [
            self.knowledge_base[kid]
            for kid in self.categories['self']
            if kid in self.knowledge_base
        ]
    
    def get_system_knowledge(self) -> List[WorldKnowledge]:
        """Get all system knowledge"""
        return [
            self.knowledge_base[kid]
            for kid in self.categories['system']
            if kid in self.knowledge_base
        ]
    
    def _load_knowledge(self):
        """Load knowledge from disk"""
        knowledge_file = self.storage_path / "world_knowledge.json"
        
        if knowledge_file.exists():
            try:
                with open(knowledge_file, 'r') as f:
                    data = json.load(f)
                    
                for k_dict in data.get('knowledge', []):
                    knowledge = WorldKnowledge(**k_dict)
                    self.knowledge_base[knowledge.knowledge_id] = knowledge
                    self.categories[knowledge.category].append(knowledge.knowledge_id)
                
                logger.info(f"[WORLD-MODEL] Loaded {len(self.knowledge_base)} knowledge items")
            except Exception as e:
                logger.error(f"[WORLD-MODEL] Failed to load knowledge: {e}")
    
    def _save_knowledge(self):
        """Save knowledge to disk"""
        knowledge_file = self.storage_path / "world_knowledge.json"
        
        try:
            data = {
                'knowledge': [k.to_dict() for k in self.knowledge_base.values()],
                'saved_at': datetime.utcnow().isoformat()
            }
            
            with open(knowledge_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"[WORLD-MODEL] Failed to save knowledge: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get world model statistics"""
        return {
            'total_knowledge': len(self.knowledge_base),
            'by_category': {
                cat: len(items)
                for cat, items in self.categories.items()
            },
            'most_accessed': sorted(
                self.knowledge_base.values(),
                key=lambda k: k.access_count,
                reverse=True
            )[:5],
            'average_confidence': sum(k.confidence for k in self.knowledge_base.values()) / len(self.knowledge_base) if self.knowledge_base else 0
        }


# Singleton instance
grace_world_model = GraceWorldModel()
