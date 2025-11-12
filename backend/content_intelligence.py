"""
Content Intelligence Layer
Provides duplicate detection, drift analysis, quality scoring, and recommendations
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import hashlib
import json
from difflib import SequenceMatcher
from pathlib import Path

from backend.clarity import BaseComponent, ComponentStatus, get_event_bus, Event


class ContentIntelligence(BaseComponent):
    """
    Intelligent content analysis and recommendations
    """
    
    def __init__(self):
        super().__init__()
        self.component_type = "content_intelligence"
        self.event_bus = get_event_bus()
        self.content_index: Dict[str, Dict] = {}  # path -> analysis
        self.similarity_threshold = 0.85
        
    async def activate(self) -> bool:
        """Activate content intelligence"""
        self.set_status(ComponentStatus.ACTIVE)
        self.activated_at = datetime.utcnow()
        
        await self.event_bus.publish(Event(
            event_type="intelligence.activated",
            source=self.component_id,
            payload={"component": self.component_type}
        ))
        
        return True
    
    async def analyze_file(
        self, 
        file_path: str, 
        content: str,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Comprehensive file analysis
        Returns: quality score, duplicates, recommendations
        """
        
        analysis = {
            "path": file_path,
            "analyzed_at": datetime.utcnow().isoformat(),
            "content_hash": self._compute_hash(content),
            "size": len(content),
            "line_count": len(content.split('\n')),
            "word_count": len(content.split()),
            "quality_score": 0.0,
            "issues": [],
            "recommendations": [],
            "duplicates": [],
            "similar_files": [],
            "tags_suggested": [],
            "domain_suggested": None,
            "trust_level": "unknown"
        }
        
        # Quality scoring
        quality = self._assess_quality(content, file_path)
        analysis["quality_score"] = quality["score"]
        analysis["issues"] = quality["issues"]
        
        # Duplicate detection
        duplicates = await self._find_duplicates(content, file_path)
        analysis["duplicates"] = duplicates
        
        # Similar content
        similar = await self._find_similar(content, file_path)
        analysis["similar_files"] = similar
        
        # Auto-tagging
        tags = self._suggest_tags(content, file_path, metadata)
        analysis["tags_suggested"] = tags
        
        # Domain classification
        domain = self._classify_domain(content, file_path)
        analysis["domain_suggested"] = domain
        
        # Trust assessment
        trust = self._assess_trust(content, metadata)
        analysis["trust_level"] = trust
        
        # Recommendations
        recommendations = self._generate_recommendations(analysis)
        analysis["recommendations"] = recommendations
        
        # Store in index
        self.content_index[file_path] = analysis
        
        # Publish analysis event
        await self.event_bus.publish(Event(
            event_type="intelligence.file.analyzed",
            source=self.component_id,
            payload={
                "path": file_path,
                "quality_score": analysis["quality_score"],
                "duplicates_found": len(duplicates),
                "recommendations": len(recommendations)
            }
        ))
        
        return analysis
    
    def _compute_hash(self, content: str) -> str:
        """Compute content hash for duplicate detection"""
        return hashlib.sha256(content.encode()).hexdigest()
    
    def _assess_quality(self, content: str, file_path: str) -> Dict[str, Any]:
        """
        Assess content quality
        Returns score 0-100 and list of issues
        """
        score = 100.0
        issues = []
        
        # Check for minimum length
        if len(content) < 50:
            score -= 30
            issues.append("Content too short (< 50 chars)")
        
        # Check for proper encoding
        try:
            content.encode('utf-8')
        except UnicodeEncodeError:
            score -= 20
            issues.append("Encoding issues detected")
        
        # Check for excessive whitespace
        lines = content.split('\n')
        empty_lines = sum(1 for line in lines if not line.strip())
        if empty_lines > len(lines) * 0.5:
            score -= 15
            issues.append("Excessive empty lines")
        
        # Check for structured content (code, markdown)
        ext = Path(file_path).suffix.lower()
        if ext in ['.py', '.js', '.ts']:
            # Check for basic code structure
            if 'def ' not in content and 'function ' not in content and 'class ' not in content:
                score -= 10
                issues.append("Code file lacks structure")
        
        if ext in ['.md', '.markdown']:
            # Check for markdown headers
            if not any(line.startswith('#') for line in lines):
                score -= 10
                issues.append("Markdown missing headers")
        
        # Check for potential issues
        if len(content) > 1000000:  # > 1MB
            issues.append("Large file - consider splitting")
        
        # Binary content detection
        try:
            content.encode('ascii')
        except UnicodeEncodeError:
            # Has non-ASCII, might be intentional or binary
            binary_ratio = sum(1 for c in content if ord(c) > 127) / len(content)
            if binary_ratio > 0.3:
                score -= 50
                issues.append("High binary content ratio - not text?")
        
        return {
            "score": max(0, min(100, score)),
            "issues": issues
        }
    
    async def _find_duplicates(self, content: str, file_path: str) -> List[str]:
        """Find exact duplicate files"""
        content_hash = self._compute_hash(content)
        duplicates = []
        
        for path, analysis in self.content_index.items():
            if path == file_path:
                continue
            if analysis["content_hash"] == content_hash:
                duplicates.append(path)
        
        return duplicates
    
    async def _find_similar(
        self, 
        content: str, 
        file_path: str, 
        threshold: float = None
    ) -> List[Tuple[str, float]]:
        """
        Find similar files using sequence matching
        Returns list of (path, similarity_score) tuples
        """
        if threshold is None:
            threshold = self.similarity_threshold
        
        similar = []
        
        for path, analysis in self.content_index.items():
            if path == file_path:
                continue
            
            # For performance, only compare if size is similar
            size_ratio = analysis["size"] / max(len(content), 1)
            if size_ratio < 0.5 or size_ratio > 2.0:
                continue
            
            # Compare first 1000 chars for speed
            sample_size = min(1000, len(content))
            
            # Would need to fetch other file's content in real implementation
            # For now, just use a stub similarity score
            similarity = 0.7  # Stub
            
            if similarity >= threshold:
                similar.append((path, similarity))
        
        return sorted(similar, key=lambda x: x[1], reverse=True)[:5]
    
    def _suggest_tags(
        self, 
        content: str, 
        file_path: str, 
        metadata: Optional[Dict]
    ) -> List[str]:
        """Auto-suggest tags based on content analysis"""
        tags = []
        ext = Path(file_path).suffix.lower()
        
        # File type tags
        type_tags = {
            '.py': ['python', 'code', 'script'],
            '.js': ['javascript', 'code', 'web'],
            '.ts': ['typescript', 'code', 'web'],
            '.md': ['markdown', 'documentation', 'text'],
            '.json': ['json', 'data', 'config'],
            '.yaml': ['yaml', 'config', 'data'],
            '.pdf': ['pdf', 'document'],
            '.txt': ['text', 'document']
        }
        
        tags.extend(type_tags.get(ext, []))
        
        # Content-based tags
        content_lower = content.lower()
        
        # Technical content
        if any(word in content_lower for word in ['api', 'endpoint', 'request', 'response']):
            tags.append('api')
        
        if any(word in content_lower for word in ['test', 'assert', 'expect']):
            tags.append('testing')
        
        if any(word in content_lower for word in ['database', 'sql', 'query']):
            tags.append('database')
        
        # Documentation
        if content_lower.count('#') > 3 or content.count('##') > 2:
            tags.append('well-documented')
        
        # Machine learning
        if any(word in content_lower for word in ['model', 'train', 'embedding', 'neural']):
            tags.append('machine-learning')
        
        # Size-based
        if len(content) > 50000:
            tags.append('large-file')
        elif len(content) < 500:
            tags.append('snippet')
        
        return list(set(tags))  # Remove duplicates
    
    def _classify_domain(self, content: str, file_path: str) -> Optional[str]:
        """Classify file into a knowledge domain"""
        content_lower = content.lower()
        
        # Domain keywords
        domains = {
            'engineering': ['code', 'function', 'class', 'import', 'module'],
            'documentation': ['guide', 'tutorial', 'how to', 'documentation', 'readme'],
            'data': ['dataset', 'csv', 'json', 'database', 'table'],
            'ml': ['model', 'train', 'embedding', 'neural', 'gradient'],
            'security': ['auth', 'password', 'token', 'encrypt', 'security'],
            'api': ['endpoint', 'route', 'request', 'response', 'api'],
            'testing': ['test', 'assert', 'mock', 'fixture', 'pytest'],
            'config': ['config', 'settings', 'environment', 'variable']
        }
        
        # Score each domain
        scores = {}
        for domain, keywords in domains.items():
            score = sum(1 for keyword in keywords if keyword in content_lower)
            if score > 0:
                scores[domain] = score
        
        if not scores:
            return 'general'
        
        # Return highest scoring domain
        return max(scores.items(), key=lambda x: x[1])[0]
    
    def _assess_trust(self, content: str, metadata: Optional[Dict]) -> str:
        """Assess trust level of content"""
        
        # Check metadata first
        if metadata and metadata.get('verified'):
            return 'verified'
        
        # Basic heuristics
        content_lower = content.lower()
        
        # Red flags
        if any(word in content_lower for word in ['todo', 'fixme', 'hack', 'temporary']):
            return 'draft'
        
        # Positive indicators
        if any(word in content_lower for word in ['tested', 'reviewed', 'approved']):
            return 'reviewed'
        
        # Has proper structure
        if len(content) > 1000 and len(content.split('\n')) > 20:
            return 'standard'
        
        return 'unverified'
    
    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Quality-based
        if analysis["quality_score"] < 50:
            recommendations.append({
                "type": "quality",
                "severity": "high",
                "message": "Content quality is low - consider reviewing and improving",
                "action": "review_content"
            })
        
        # Duplicates
        if analysis["duplicates"]:
            recommendations.append({
                "type": "duplicate",
                "severity": "medium",
                "message": f"Found {len(analysis['duplicates'])} duplicate files - consider consolidating",
                "action": "remove_duplicates",
                "details": analysis["duplicates"][:3]  # Show first 3
            })
        
        # Similar files
        if analysis["similar_files"]:
            recommendations.append({
                "type": "similarity",
                "severity": "low",
                "message": f"Found {len(analysis['similar_files'])} similar files - check for updates",
                "action": "review_similar",
                "details": [f[0] for f in analysis["similar_files"][:3]]
            })
        
        # Size recommendations
        if analysis["size"] > 1000000:
            recommendations.append({
                "type": "size",
                "severity": "medium",
                "message": "Large file detected - consider splitting for better processing",
                "action": "split_file"
            })
        
        # Trust recommendations
        if analysis["trust_level"] in ["draft", "unverified"]:
            recommendations.append({
                "type": "trust",
                "severity": "medium",
                "message": f"Trust level: {analysis['trust_level']} - review before syncing to Memory Fusion",
                "action": "verify_content"
            })
        
        # Domain recommendations
        if analysis["domain_suggested"]:
            recommendations.append({
                "type": "classification",
                "severity": "info",
                "message": f"Suggested domain: {analysis['domain_suggested']}",
                "action": "apply_domain_tag"
            })
        
        return recommendations
    
    async def get_insights(self) -> Dict[str, Any]:
        """Get overall content insights"""
        
        total_files = len(self.content_index)
        if total_files == 0:
            return {"message": "No files analyzed yet"}
        
        # Aggregate statistics
        total_size = sum(a["size"] for a in self.content_index.values())
        avg_quality = sum(a["quality_score"] for a in self.content_index.values()) / total_files
        
        duplicates_count = sum(
            1 for a in self.content_index.values() if a["duplicates"]
        )
        
        # Domain distribution
        domains = {}
        for analysis in self.content_index.values():
            domain = analysis["domain_suggested"]
            if domain:
                domains[domain] = domains.get(domain, 0) + 1
        
        # Trust levels
        trust_levels = {}
        for analysis in self.content_index.values():
            level = analysis["trust_level"]
            trust_levels[level] = trust_levels.get(level, 0) + 1
        
        # Quality distribution
        quality_ranges = {"high": 0, "medium": 0, "low": 0}
        for analysis in self.content_index.values():
            score = analysis["quality_score"]
            if score >= 80:
                quality_ranges["high"] += 1
            elif score >= 50:
                quality_ranges["medium"] += 1
            else:
                quality_ranges["low"] += 1
        
        return {
            "total_files": total_files,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "average_quality": round(avg_quality, 2),
            "files_with_duplicates": duplicates_count,
            "domain_distribution": domains,
            "trust_levels": trust_levels,
            "quality_distribution": quality_ranges,
            "analyzed_at": datetime.utcnow().isoformat()
        }


# Global instance
_content_intelligence: Optional[ContentIntelligence] = None


async def get_content_intelligence() -> ContentIntelligence:
    """Get or create global content intelligence"""
    global _content_intelligence
    if _content_intelligence is None:
        _content_intelligence = ContentIntelligence()
        await _content_intelligence.activate()
    return _content_intelligence
