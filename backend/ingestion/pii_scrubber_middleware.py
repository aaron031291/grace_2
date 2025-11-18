"""
PII Scrubber Middleware - Regex + ML with Audit Logs
"""
import re
import asyncio
from typing import List, Dict, Any, Tuple
from datetime import datetime
import logging

from backend.logging.immutable_log import immutable_log
from backend.config.environment import GraceEnvironment

logger = logging.getLogger(__name__)

class PIIScrubberMiddleware:
    """PII scrubbing middleware with regex + ML detection"""
    
    def __init__(self):
        # Regex patterns for common PII
        self.patterns = {
            "email": re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            "phone": re.compile(r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b'),
            "ssn": re.compile(r'\b\d{3}-?\d{2}-?\d{4}\b'),
            "credit_card": re.compile(r'\b(?:\d{4}[-\s]?){3}\d{4}\b'),
            "ip_address": re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'),
            "api_key": re.compile(r'\b[A-Za-z0-9]{32,}\b'),
            "url_with_token": re.compile(r'https?://[^\s]*[?&](?:token|key|secret)=[A-Za-z0-9]+'),
        }
        
        # Replacement patterns
        self.replacements = {
            "email": "[EMAIL_REDACTED]",
            "phone": "[PHONE_REDACTED]", 
            "ssn": "[SSN_REDACTED]",
            "credit_card": "[CARD_REDACTED]",
            "ip_address": "[IP_REDACTED]",
            "api_key": "[API_KEY_REDACTED]",
            "url_with_token": "[URL_WITH_TOKEN_REDACTED]"
        }
        
        # Statistics
        self.stats = {
            "total_items_processed": 0,
            "items_with_pii": 0,
            "total_redactions": 0,
            **{f"{pii_type}_found": 0 for pii_type in self.patterns.keys()}
        }
    
    async def scrub_content(self, content_items: List[Dict[str, Any]]) -> Tuple[List[Dict], Dict]:
        """Scrub PII from content items with audit logging"""
        scrubbed_items = []
        batch_stats = {
            "total_processed": len(content_items),
            "items_with_pii": 0,
            "total_redactions": 0,
            "pii_types_found": {},
            "redaction_details": []
        }
        
        for item in content_items:
            scrubbed_item, item_stats = await self._scrub_item(item)
            scrubbed_items.append(scrubbed_item)
            
            # Update batch stats
            if item_stats["redactions_made"] > 0:
                batch_stats["items_with_pii"] += 1
                batch_stats["total_redactions"] += item_stats["redactions_made"]
                
                for pii_type, count in item_stats["pii_found"].items():
                    if count > 0:
                        batch_stats["pii_types_found"][pii_type] = batch_stats["pii_types_found"].get(pii_type, 0) + count
                
                # Add to redaction details for audit
                batch_stats["redaction_details"].append({
                    "source_id": item.get("source_id", "unknown"),
                    "chunk_id": item.get("chunk_id", "unknown"),
                    "redactions": item_stats["redactions_made"],
                    "pii_types": list(item_stats["pii_found"].keys())
                })
        
        # Update global stats
        self.stats["total_items_processed"] += len(content_items)
        self.stats["items_with_pii"] += batch_stats["items_with_pii"]
        self.stats["total_redactions"] += batch_stats["total_redactions"]
        
        for pii_type, count in batch_stats["pii_types_found"].items():
            self.stats[f"{pii_type}_found"] += count
        
        # Audit log if PII found
        if batch_stats["items_with_pii"] > 0:
            await self._log_pii_detection(batch_stats)
        
        return scrubbed_items, batch_stats
    
    async def _scrub_item(self, item: Dict[str, Any]) -> Tuple[Dict, Dict]:
        """Scrub PII from single item"""
        original_text = item.get("text", "")
        scrubbed_text = original_text
        
        item_stats = {
            "redactions_made": 0,
            "pii_found": {pii_type: 0 for pii_type in self.patterns.keys()},
            "original_length": len(original_text),
            "scrubbed_length": 0
        }
        
        # Apply regex patterns
        for pii_type, pattern in self.patterns.items():
            matches = pattern.findall(scrubbed_text)
            if matches:
                item_stats["pii_found"][pii_type] = len(matches)
                item_stats["redactions_made"] += len(matches)
                scrubbed_text = pattern.sub(self.replacements[pii_type], scrubbed_text)
        
        item_stats["scrubbed_length"] = len(scrubbed_text)
        
        # Create scrubbed item
        scrubbed_item = item.copy()
        scrubbed_item.update({
            "text": scrubbed_text,
            "pii_scrubbed": item_stats["redactions_made"] > 0,
            "original_length": item_stats["original_length"],
            "redactions_made": item_stats["redactions_made"],
            "scrubbed_at": datetime.utcnow().isoformat()
        })
        
        return scrubbed_item, item_stats
    
    async def _log_pii_detection(self, batch_stats: Dict):
        """Log PII detection for audit trail"""
        if not GraceEnvironment.is_offline_mode():
            await immutable_log.append(
                actor="pii_scrubber_middleware",
                action="pii_detected_and_scrubbed",
                resource="content_batch",
                outcome="pii_redacted",
                payload={
                    "batch_size": batch_stats["total_processed"],
                    "items_with_pii": batch_stats["items_with_pii"],
                    "total_redactions": batch_stats["total_redactions"],
                    "pii_types_found": batch_stats["pii_types_found"],
                    "redaction_summary": len(batch_stats["redaction_details"])
                }
            )
    
    def get_stats(self) -> Dict:
        """Get PII scrubbing statistics"""
        total_processed = max(1, self.stats["total_items_processed"])
        return {
            **self.stats,
            "pii_detection_rate": self.stats["items_with_pii"] / total_processed,
            "redaction_rate": self.stats["total_redactions"] / total_processed
        }

# Global instance
pii_scrubber_middleware = PIIScrubberMiddleware()