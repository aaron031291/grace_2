"""
Content Deduplicator - Phase 2
Dedupe via content fingerprints and source fingerprints
"""
import hashlib
import asyncio
from typing import Dict, List, Any, Set, Optional
from datetime import datetime
import json

class ContentDeduplicator:
    """Production deduplication with content and source fingerprints"""
    
    def __init__(self):
        self.content_fingerprints: Set[str] = set()
        self.source_fingerprints: Dict[str, Dict] = {}
        self.duplicate_stats = {
            "total_items_processed": 0,
            "content_duplicates_found": 0,
            "source_duplicates_found": 0,
            "deduplication_rate": 0.0,
            "fingerprint_cache_size": 0
        }
    
    async def deduplicate_batch(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Deduplicate a batch of content items"""
        unique_items = []
        
        for item in items:
            is_duplicate, duplicate_type = await self._check_duplicate(item)
            
            if not is_duplicate:
                unique_items.append(item)
                await self._store_fingerprints(item)
            else:
                self._update_duplicate_stats(duplicate_type)
        
        self._update_deduplication_rate(len(items), len(unique_items))
        return unique_items
    
    async def _check_duplicate(self, item: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Check if item is duplicate by content or source"""
        
        # Generate content fingerprint
        content_fingerprint = await self._generate_content_fingerprint(item)
        if content_fingerprint in self.content_fingerprints:
            return True, "content_duplicate"
        
        # Generate source fingerprint
        source_fingerprint = await self._generate_source_fingerprint(item)
        source_id = item.get("source_id", "unknown")
        
        if source_id in self.source_fingerprints:
            existing_fingerprint = self.source_fingerprints[source_id]["fingerprint"]
            if existing_fingerprint == source_fingerprint:
                return True, "source_duplicate"
        
        return False, None
    
    async def _generate_content_fingerprint(self, item: Dict[str, Any]) -> str:
        """Generate content-based fingerprint using simhash"""
        content = item.get("text", "") + item.get("title", "")
        
        # Normalize content
        normalized = content.lower().strip()
        normalized = " ".join(normalized.split())  # Normalize whitespace
        
        # Generate hash
        content_hash = hashlib.sha256(normalized.encode()).hexdigest()
        
        # Simhash for near-duplicate detection
        simhash = await self._calculate_simhash(normalized)
        
        return f"{content_hash[:16]}_{simhash}"
    
    async def _generate_source_fingerprint(self, item: Dict[str, Any]) -> str:
        """Generate source-based fingerprint"""
        source_data = {
            "url": item.get("url", ""),
            "file_path": item.get("file_path", ""),
            "last_modified": item.get("last_modified", ""),
            "file_size": item.get("file_size", 0),
            "content_type": item.get("content_type", "")
        }
        
        fingerprint_string = json.dumps(source_data, sort_keys=True)
        return hashlib.md5(fingerprint_string.encode()).hexdigest()
    
    async def _calculate_simhash(self, text: str) -> str:
        """Calculate simhash for near-duplicate detection"""
        # Simple simhash implementation
        words = text.split()
        hash_bits = [0] * 64
        
        for word in words:
            word_hash = int(hashlib.md5(word.encode()).hexdigest(), 16)
            
            for i in range(64):
                if word_hash & (1 << i):
                    hash_bits[i] += 1
                else:
                    hash_bits[i] -= 1
        
        simhash = 0
        for i in range(64):
            if hash_bits[i] > 0:
                simhash |= (1 << i)
        
        return hex(simhash)[2:]
    
    async def _store_fingerprints(self, item: Dict[str, Any]):
        """Store fingerprints for future deduplication"""
        content_fingerprint = await self._generate_content_fingerprint(item)
        source_fingerprint = await self._generate_source_fingerprint(item)
        source_id = item.get("source_id", "unknown")
        
        self.content_fingerprints.add(content_fingerprint)
        self.source_fingerprints[source_id] = {
            "fingerprint": source_fingerprint,
            "stored_at": datetime.now().isoformat(),
            "item_count": self.source_fingerprints.get(source_id, {}).get("item_count", 0) + 1
        }
        
        self.duplicate_stats["fingerprint_cache_size"] = len(self.content_fingerprints)
    
    def _update_duplicate_stats(self, duplicate_type: str):
        """Update duplicate statistics"""
        self.duplicate_stats["total_items_processed"] += 1
        
        if duplicate_type == "content_duplicate":
            self.duplicate_stats["content_duplicates_found"] += 1
        elif duplicate_type == "source_duplicate":
            self.duplicate_stats["source_duplicates_found"] += 1
    
    def _update_deduplication_rate(self, total_items: int, unique_items: int):
        """Update overall deduplication rate"""
        if total_items > 0:
            duplicates_found = total_items - unique_items
            self.duplicate_stats["deduplication_rate"] = duplicates_found / total_items
    
    async def get_deduplication_metrics(self) -> Dict[str, Any]:
        """Get deduplication metrics"""
        return {
            "stats": self.duplicate_stats,
            "cache_info": {
                "content_fingerprints": len(self.content_fingerprints),
                "source_fingerprints": len(self.source_fingerprints)
            },
            "recommendations": self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on deduplication patterns"""
        recommendations = []
        
        if self.duplicate_stats["deduplication_rate"] > 0.3:
            recommendations.append("High duplication rate detected - review content sources")
        
        if len(self.content_fingerprints) > 100000:
            recommendations.append("Consider implementing fingerprint cleanup policy")
        
        return recommendations

content_deduplicator = ContentDeduplicator()
