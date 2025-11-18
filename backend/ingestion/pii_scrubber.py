"""
PII Scrubber - Phase 2
Remove/mask PII from content with metrics
"""
import re
import hashlib
from typing import Dict, List, Any, Tuple
from datetime import datetime

class PIIScrubber:
    """Production PII scrubbing with pattern detection and metrics"""
    
    def __init__(self):
        # PII patterns (locked for consistency)
        self.pii_patterns = {
            "ssn": re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
            "phone": re.compile(r'\b\d{3}-\d{3}-\d{4}\b'),
            "email": re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            "credit_card": re.compile(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'),
            "ip_address": re.compile(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'),
            "date_of_birth": re.compile(r'\b\d{1,2}/\d{1,2}/\d{4}\b'),
            "address": re.compile(r'\b\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln)\b', re.IGNORECASE)
        }
        
        self.scrubbing_stats = {
            "total_items_processed": 0,
            "items_with_pii": 0,
            "pii_instances_found": 0,
            "pii_detection_rate": 0.0,
            "pattern_breakdown": {pattern: 0 for pattern in self.pii_patterns.keys()}
        }
    
    async def scrub_content(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Scrub PII from content item"""
        scrubbed_item = item.copy()
        original_text = item.get("text", "")
        
        if not original_text:
            return scrubbed_item
        
        scrubbed_text, pii_found = await self._scrub_text(original_text)
        
        # Update item if PII was found
        if pii_found:
            scrubbed_item["text"] = scrubbed_text
            scrubbed_item["pii_scrubbed"] = True
            scrubbed_item["original_length"] = len(original_text)
            scrubbed_item["scrubbed_length"] = len(scrubbed_text)
            scrubbed_item["pii_patterns_found"] = list(pii_found.keys())
            
            self._update_pii_stats(pii_found)
        else:
            scrubbed_item["pii_scrubbed"] = False
        
        self.scrubbing_stats["total_items_processed"] += 1
        return scrubbed_item
    
    async def _scrub_text(self, text: str) -> Tuple[str, Dict[str, int]]:
        """Scrub PII patterns from text"""
        scrubbed_text = text
        pii_found = {}
        
        for pattern_name, pattern in self.pii_patterns.items():
            matches = pattern.findall(text)
            
            if matches:
                pii_found[pattern_name] = len(matches)
                
                # Replace with masked version
                for match in matches:
                    mask = await self._generate_mask(match, pattern_name)
                    scrubbed_text = scrubbed_text.replace(match, mask)
        
        return scrubbed_text, pii_found
    
    async def _generate_mask(self, original: str, pattern_type: str) -> str:
        """Generate appropriate mask for PII type"""
        masks = {
            "ssn": "XXX-XX-XXXX",
            "phone": "XXX-XXX-XXXX", 
            "email": "[EMAIL_REDACTED]",
            "credit_card": "XXXX-XXXX-XXXX-XXXX",
            "ip_address": "XXX.XXX.XXX.XXX",
            "date_of_birth": "XX/XX/XXXX",
            "address": "[ADDRESS_REDACTED]"
        }
        
        return masks.get(pattern_type, "[PII_REDACTED]")
    
    def _update_pii_stats(self, pii_found: Dict[str, int]):
        """Update PII detection statistics"""
        self.scrubbing_stats["items_with_pii"] += 1
        
        total_pii_instances = sum(pii_found.values())
        self.scrubbing_stats["pii_instances_found"] += total_pii_instances
        
        # Update pattern breakdown
        for pattern, count in pii_found.items():
            self.scrubbing_stats["pattern_breakdown"][pattern] += count
        
        # Update detection rate
        if self.scrubbing_stats["total_items_processed"] > 0:
            self.scrubbing_stats["pii_detection_rate"] = (
                self.scrubbing_stats["items_with_pii"] / 
                self.scrubbing_stats["total_items_processed"]
            )
    
    async def get_pii_metrics(self) -> Dict[str, Any]:
        """Get PII scrubbing metrics"""
        return {
            "stats": self.scrubbing_stats,
            "pattern_analysis": self._analyze_patterns(),
            "recommendations": self._generate_recommendations()
        }
    
    def _analyze_patterns(self) -> Dict[str, Any]:
        """Analyze PII pattern distribution"""
        total_patterns = sum(self.scrubbing_stats["pattern_breakdown"].values())
        
        if total_patterns == 0:
            return {"distribution": {}, "most_common": None}
        
        distribution = {
            pattern: count / total_patterns 
            for pattern, count in self.scrubbing_stats["pattern_breakdown"].items()
        }
        
        most_common = max(
            self.scrubbing_stats["pattern_breakdown"].items(),
            key=lambda x: x[1]
        )[0]
        
        return {
            "distribution": distribution,
            "most_common": most_common,
            "total_patterns_found": total_patterns
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on PII patterns"""
        recommendations = []
        
        if self.scrubbing_stats["pii_detection_rate"] > 0.05:
            recommendations.append("High PII detection rate - review data sources")
        
        most_common_pattern = max(
            self.scrubbing_stats["pattern_breakdown"].items(),
            key=lambda x: x[1],
            default=(None, 0)
        )
        
        if most_common_pattern[1] > 10:
            recommendations.append(f"Consider enhanced filtering for {most_common_pattern[0]} patterns")
        
        return recommendations

pii_scrubber = PIIScrubber()