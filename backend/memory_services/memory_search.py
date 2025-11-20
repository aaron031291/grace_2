"""
Memory Search Engine
Full-text, semantic, and metadata-based search across Grace's memory
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import re

from backend.clarity import BaseComponent, ComponentStatus, get_event_bus, Event
from backend.core.unified_event_publisher import publish_event_obj


class SearchResult:
    """Represents a search result"""
    
    def __init__(
        self,
        file_path: str,
        score: float,
        matches: List[Dict],
        metadata: Optional[Dict] = None
    ):
        self.file_path = file_path
        self.score = score
        self.matches = matches
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict:
        return {
            "file_path": self.file_path,
            "score": self.score,
            "matches": self.matches,
            "metadata": self.metadata
        }


class MemorySearchEngine(BaseComponent):
    """
    Advanced search capabilities for Memory Studio
    """
    
    def __init__(self):
        super().__init__()
        self.component_type = "memory_search"
        self.event_bus = get_event_bus()
        self.index: Dict[str, Dict] = {}  # file_path -> indexed_data
        
    async def activate(self) -> bool:
        """Activate search engine"""
        self.set_status(ComponentStatus.ACTIVE)
        self.activated_at = datetime.utcnow()
        
        await publish_event_obj(Event(
            event_type="search.engine.activated",
            source=self.component_id,
            payload={"component": self.component_type}
        ))
        
        return True
    
    async def index_file(
        self,
        file_path: str,
        content: str,
        metadata: Optional[Dict] = None
    ):
        """
        Index a file for searching
        Creates inverted index for fast lookup
        """
        
        # Tokenize content
        words = re.findall(r'\w+', content.lower())
        word_positions = {}
        
        for pos, word in enumerate(words):
            if word not in word_positions:
                word_positions[word] = []
            word_positions[word].append(pos)
        
        # Store in index
        self.index[file_path] = {
            "content_length": len(content),
            "word_count": len(words),
            "word_positions": word_positions,
            "metadata": metadata or {},
            "indexed_at": datetime.utcnow().isoformat(),
            "preview": content[:200]  # First 200 chars
        }
    
    async def search(
        self,
        query: str,
        search_type: str = "text",  # text, metadata, semantic
        filters: Optional[Dict] = None,
        limit: int = 50
    ) -> List[SearchResult]:
        """
        Search across indexed files
        
        Args:
            query: Search query
            search_type: Type of search (text, metadata, semantic)
            filters: Additional filters (category, domain, tags)
            limit: Max results
        """
        
        results = []
        
        if search_type == "text":
            results = await self._text_search(query, filters)
        elif search_type == "metadata":
            results = await self._metadata_search(query, filters)
        elif search_type == "semantic":
            results = await self._semantic_search(query, filters)
        else:
            # Multi-search: combine all methods
            text_results = await self._text_search(query, filters)
            meta_results = await self._metadata_search(query, filters)
            results = text_results + meta_results
        
        # Sort by score and limit
        results.sort(key=lambda r: r.score, reverse=True)
        return results[:limit]
    
    async def _text_search(
        self,
        query: str,
        filters: Optional[Dict] = None
    ) -> List[SearchResult]:
        """Full-text search across content"""
        
        query_words = set(re.findall(r'\w+', query.lower()))
        results = []
        
        for file_path, indexed_data in self.index.items():
            # Apply filters
            if filters and not self._matches_filters(indexed_data, filters):
                continue
            
            # Calculate match score
            word_positions = indexed_data["word_positions"]
            matched_words = query_words.intersection(word_positions.keys())
            
            if not matched_words:
                continue
            
            # Score = percentage of query words found
            score = len(matched_words) / len(query_words)
            
            # Bonus for multiple occurrences
            total_occurrences = sum(len(word_positions[w]) for w in matched_words)
            score += min(total_occurrences * 0.01, 0.3)  # Up to 30% bonus
            
            # Create matches list
            matches = [
                {
                    "word": word,
                    "count": len(word_positions[word]),
                    "positions": word_positions[word][:5]  # First 5 positions
                }
                for word in matched_words
            ]
            
            results.append(SearchResult(
                file_path=file_path,
                score=min(score, 1.0),
                matches=matches,
                metadata=indexed_data["metadata"]
            ))
        
        return results
    
    async def _metadata_search(
        self,
        query: str,
        filters: Optional[Dict] = None
    ) -> List[SearchResult]:
        """Search in metadata (tags, domain, etc.)"""
        
        query_lower = query.lower()
        results = []
        
        for file_path, indexed_data in self.index.items():
            metadata = indexed_data.get("metadata", {})
            
            # Apply filters
            if filters and not self._matches_filters(indexed_data, filters):
                continue
            
            score = 0.0
            matches = []
            
            # Check tags
            tags = metadata.get("tags", [])
            for tag in tags:
                if query_lower in tag.lower():
                    score += 0.3
                    matches.append({"field": "tag", "value": tag})
            
            # Check domain
            domain = metadata.get("domain", "")
            if query_lower in domain.lower():
                score += 0.4
                matches.append({"field": "domain", "value": domain})
            
            # Check category
            category = metadata.get("category", "")
            if query_lower in category.lower():
                score += 0.3
                matches.append({"field": "category", "value": category})
            
            if score > 0:
                results.append(SearchResult(
                    file_path=file_path,
                    score=min(score, 1.0),
                    matches=matches,
                    metadata=metadata
                ))
        
        return results
    
    async def _semantic_search(
        self,
        query: str,
        filters: Optional[Dict] = None
    ) -> List[SearchResult]:
        """
        Semantic search using embeddings
        (Stub - requires embedding generation)
        """
        
        # TODO: Implement with actual embeddings
        # For now, return empty
        return []
    
    def _matches_filters(self, indexed_data: Dict, filters: Dict) -> bool:
        """Check if file matches filter criteria"""
        
        metadata = indexed_data.get("metadata", {})
        
        # Category filter
        if "category" in filters:
            if metadata.get("category") != filters["category"]:
                return False
        
        # Domain filter
        if "domain" in filters:
            if metadata.get("domain") != filters["domain"]:
                return False
        
        # Tags filter (any match)
        if "tags" in filters:
            file_tags = set(metadata.get("tags", []))
            filter_tags = set(filters["tags"])
            if not file_tags.intersection(filter_tags):
                return False
        
        # Trust level filter
        if "trust_level" in filters:
            if metadata.get("trust_level") != filters["trust_level"]:
                return False
        
        # Min quality filter
        if "min_quality" in filters:
            quality = metadata.get("quality_score", 0)
            if quality < filters["min_quality"]:
                return False
        
        return True
    
    def get_index_stats(self) -> Dict[str, Any]:
        """Get search index statistics"""
        
        total_files = len(self.index)
        total_words = sum(data["word_count"] for data in self.index.values())
        unique_words = set()
        
        for data in self.index.values():
            unique_words.update(data["word_positions"].keys())
        
        return {
            "total_files_indexed": total_files,
            "total_words": total_words,
            "unique_words": len(unique_words),
            "avg_words_per_file": total_words // max(total_files, 1),
            "index_size_estimate": len(str(self.index))
        }


# Global instance
_search_engine: Optional[MemorySearchEngine] = None


async def get_search_engine() -> MemorySearchEngine:
    """Get or create global search engine"""
    global _search_engine
    if _search_engine is None:
        _search_engine = MemorySearchEngine()
        await _search_engine.activate()
    return _search_engine
