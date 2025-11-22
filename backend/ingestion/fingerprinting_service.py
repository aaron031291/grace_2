"""
Fingerprinting Service - Content + Source Deduplication
"""
import hashlib
import asyncio
from typing import Dict, List, Set, Tuple, Any
from datetime import datetime, timedelta
import logging

from backend.logging_system.immutable_log import immutable_log

logger = logging.getLogger(__name__)

class FingerprintingService:
    """Content fingerprinting with source tracking"""
    
    def __init__(self):
        self.fingerprints: Dict[str, Dict] = {}  # fingerprint -> metadata
        self.source_fingerprints: Dict[str, Set[str]] = {}  # source_id -> fingerprints
        self.stats = {
            "total_fingerprints": 0,
            "duplicates_detected": 0,
            "sources_tracked": 0,
            "cache_hits": 0,
            "cache_misses": 0
        }
    
    def generate_fingerprint(self, content: str, source_id: str, 
                           include_source: bool = True) -> str:
        """Generate fingerprint for content + source"""
        if include_source:
            data = f"{source_id}:{content.strip().lower()}"
        else:
            data = content.strip().lower()
        
        return hashlib.sha256(data.encode()).hexdigest()
    
    async def register_content(self, content: str, source_id: str, 
                             metadata: Dict = None) -> Dict[str, Any]:
        """Register content and return fingerprint info"""
        fingerprint = self.generate_fingerprint(content, source_id)
        content_only_fp = self.generate_fingerprint(content, source_id, include_source=False)
        
        result = {
            "fingerprint": fingerprint,
            "content_fingerprint": content_only_fp,
            "is_duplicate": False,
            "duplicate_source": None,
            "first_seen": datetime.utcnow().isoformat()
        }
        
        # Check for exact duplicate (content + source)
        if fingerprint in self.fingerprints:
            self.stats["duplicates_detected"] += 1
            self.stats["cache_hits"] += 1
            existing = self.fingerprints[fingerprint]
            result.update({
                "is_duplicate": True,
                "duplicate_source": existing["source_id"],
                "first_seen": existing["first_seen"]
            })
            return result
        
        # Check for content duplicate (different source)
        content_duplicate = None
        for fp, data in self.fingerprints.items():
            if data.get("content_fingerprint") == content_only_fp:
                content_duplicate = data
                break
        
        if content_duplicate:
            result["content_duplicate"] = {
                "source_id": content_duplicate["source_id"],
                "first_seen": content_duplicate["first_seen"]
            }
        
        # Register new fingerprint
        self.fingerprints[fingerprint] = {
            "content_fingerprint": content_only_fp,
            "source_id": source_id,
            "first_seen": result["first_seen"],
            "metadata": metadata or {},
            "content_length": len(content)
        }
        
        # Track by source
        if source_id not in self.source_fingerprints:
            self.source_fingerprints[source_id] = set()
            self.stats["sources_tracked"] += 1
        
        self.source_fingerprints[source_id].add(fingerprint)
        self.stats["total_fingerprints"] += 1
        self.stats["cache_misses"] += 1
        
        return result
    
    async def check_duplicates(self, content_items: List[Dict]) -> Tuple[List[Dict], Dict]:
        """Check for duplicates in batch"""
        unique_items = []
        duplicate_stats = {
            "original_count": len(content_items),
            "unique_count": 0,
            "exact_duplicates": 0,
            "content_duplicates": 0,
            "sources_with_duplicates": set()
        }
        
        for item in content_items:
            content = item.get("text", "")
            source_id = item.get("source_id", "unknown")
            
            fp_result = await self.register_content(content, source_id, item)
            
            if fp_result["is_duplicate"]:
                duplicate_stats["exact_duplicates"] += 1
                duplicate_stats["sources_with_duplicates"].add(source_id)
                continue
            
            if "content_duplicate" in fp_result:
                duplicate_stats["content_duplicates"] += 1
                item["content_duplicate_info"] = fp_result["content_duplicate"]
            
            # Add fingerprint info to item
            item.update({
                "fingerprint": fp_result["fingerprint"],
                "content_fingerprint": fp_result["content_fingerprint"]
            })
            
            unique_items.append(item)
        
        duplicate_stats["unique_count"] = len(unique_items)
        duplicate_stats["sources_with_duplicates"] = len(duplicate_stats["sources_with_duplicates"])
        
        return unique_items, duplicate_stats
    
    def get_source_stats(self, source_id: str) -> Dict:
        """Get statistics for specific source"""
        if source_id not in self.source_fingerprints:
            return {"error": "Source not found"}
        
        fingerprints = self.source_fingerprints[source_id]
        return {
            "source_id": source_id,
            "total_fingerprints": len(fingerprints),
            "unique_content": len(set(
                self.fingerprints[fp]["content_fingerprint"] 
                for fp in fingerprints
            ))
        }
    
    def get_stats(self) -> Dict:
        """Get service statistics"""
        return {
            **self.stats,
            "duplicate_rate": self.stats["duplicates_detected"] / max(1, self.stats["total_fingerprints"]),
            "cache_hit_rate": self.stats["cache_hits"] / max(1, self.stats["cache_hits"] + self.stats["cache_misses"])
        }

# Global instance
fingerprinting_service = FingerprintingService()
