"""
Data Hygiene Pipeline - PRODUCTION
Audits data before it enters retrieval or fine-tuning to prevent corrupted memory
"""

from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import json
from pathlib import Path


class DataQualityIssue(Enum):
    """Types of data quality issues"""
    STALE_FACTS = "stale_facts"
    CONFLICTING_VERSIONS = "conflicting_versions"
    MISSING_PROVENANCE = "missing_provenance"
    INVALID_FORMAT = "invalid_format"
    DUPLICATE_CONTENT = "duplicate_content"
    LOW_QUALITY = "low_quality"
    OUTDATED = "outdated"


@dataclass
class DataAuditResult:
    """Result of data audit"""
    passed: bool
    score: float  # 0-1, quality score
    
    # Issues found
    issues: List[DataQualityIssue] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    # Details
    freshness_days: Optional[int] = None
    has_provenance: bool = False
    conflicts_detected: int = 0
    duplicates_detected: int = 0
    
    # Recommendations
    recommended_action: str = ""
    
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def to_dict(self) -> Dict:
        return {
            'passed': self.passed,
            'score': self.score,
            'issues': [i.value for i in self.issues],
            'warnings': self.warnings,
            'details': {
                'freshness_days': self.freshness_days,
                'has_provenance': self.has_provenance,
                'conflicts': self.conflicts_detected,
                'duplicates': self.duplicates_detected
            },
            'recommended_action': self.recommended_action,
            'timestamp': self.timestamp
        }


class DataHygienePipeline:
    """
    Production data hygiene pipeline
    
    Checks before data enters system:
    1. Freshness - is data recent?
    2. Conflicts - contradicts existing data?
    3. Provenance - has source/lineage?
    4. Format - valid structure?
    5. Duplicates - already exists?
    6. Quality - meets standards?
    """
    
    def __init__(
        self,
        max_age_days: int = 365,
        min_quality_score: float = 0.7,
        storage_path: str = "databases/data_hygiene"
    ):
        self.max_age_days = max_age_days
        self.min_quality_score = min_quality_score
        
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Track known data by hash
        self.content_hashes: Set[str] = set()
        
        # Track provenance
        self.provenance_registry: Dict[str, Dict] = {}
        
        # Statistics
        self.total_audits = 0
        self.passed_audits = 0
        self.failed_audits = 0
        self.quarantined_items = 0
        
        # Load existing registry
        self._load_registry()
    
    def _load_registry(self):
        """Load content registry"""
        
        registry_file = self.storage_path / "registry.json"
        
        if registry_file.exists():
            try:
                with open(registry_file, 'r') as f:
                    data = json.load(f)
                    self.content_hashes = set(data.get('hashes', []))
                    self.provenance_registry = data.get('provenance', {})
                    self.total_audits = data.get('stats', {}).get('total', 0)
                    self.passed_audits = data.get('stats', {}).get('passed', 0)
                    self.failed_audits = data.get('stats', {}).get('failed', 0)
            except Exception as e:
                print(f"[HYGIENE] Failed to load registry: {e}")
    
    def _save_registry(self):
        """Save content registry"""
        
        registry_file = self.storage_path / "registry.json"
        
        try:
            data = {
                'hashes': list(self.content_hashes),
                'provenance': self.provenance_registry,
                'stats': {
                    'total': self.total_audits,
                    'passed': self.passed_audits,
                    'failed': self.failed_audits,
                    'quarantined': self.quarantined_items
                },
                'last_updated': datetime.utcnow().isoformat()
            }
            
            with open(registry_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"[HYGIENE] Failed to save registry: {e}")
    
    async def audit(
        self,
        content: str,
        metadata: Dict,
        existing_data: Optional[List[Dict]] = None
    ) -> DataAuditResult:
        """
        Audit data before ingestion
        
        Args:
            content: The actual content
            metadata: Metadata (source, timestamp, etc.)
            existing_data: Existing data to check for conflicts
        
        Returns:
            DataAuditResult with pass/fail and issues
        """
        
        self.total_audits += 1
        
        issues = []
        warnings = []
        score = 1.0
        
        # Check 1: Freshness
        freshness_result = self._check_freshness(metadata)
        if freshness_result['issue']:
            issues.append(DataQualityIssue.STALE_FACTS)
            score -= 0.2
        if freshness_result['warning']:
            warnings.append(freshness_result['warning'])
        
        # Check 2: Provenance
        provenance_result = self._check_provenance(metadata)
        if not provenance_result['has_provenance']:
            issues.append(DataQualityIssue.MISSING_PROVENANCE)
            score -= 0.3
        
        # Check 3: Format validation
        format_result = self._check_format(content, metadata)
        if not format_result['valid']:
            issues.append(DataQualityIssue.INVALID_FORMAT)
            score -= 0.2
            warnings.append(format_result['reason'])
        
        # Check 4: Duplicates
        duplicate_result = self._check_duplicates(content)
        if duplicate_result['is_duplicate']:
            issues.append(DataQualityIssue.DUPLICATE_CONTENT)
            score -= 0.1
        
        # Check 5: Conflicts with existing data
        conflict_result = await self._check_conflicts(content, existing_data)
        if conflict_result['conflicts'] > 0:
            issues.append(DataQualityIssue.CONFLICTING_VERSIONS)
            score -= 0.3
            warnings.append(f"{conflict_result['conflicts']} conflicts detected")
        
        # Check 6: Quality assessment
        quality_result = self._assess_quality(content, metadata)
        if quality_result['score'] < self.min_quality_score:
            issues.append(DataQualityIssue.LOW_QUALITY)
            score *= quality_result['score']  # Reduce by quality score
        
        # Final score
        score = max(0.0, score)
        
        # Determine if passed
        passed = score >= self.min_quality_score and len(issues) == 0
        
        # Update statistics
        if passed:
            self.passed_audits += 1
            # Register content
            content_hash = self._hash_content(content)
            self.content_hashes.add(content_hash)
            
            # Register provenance
            if provenance_result['has_provenance']:
                self.provenance_registry[content_hash] = provenance_result['provenance']
        else:
            self.failed_audits += 1
            if score < 0.3:
                self.quarantined_items += 1
        
        # Recommend action
        recommended_action = ""
        if not passed:
            if DataQualityIssue.CONFLICTING_VERSIONS in issues:
                recommended_action = "Resolve conflicts before ingestion"
            elif DataQualityIssue.MISSING_PROVENANCE in issues:
                recommended_action = "Add source information"
            elif DataQualityIssue.STALE_FACTS in issues:
                recommended_action = "Refresh data from source"
            elif DataQualityIssue.DUPLICATE_CONTENT in issues:
                recommended_action = "Skip - already have this content"
            else:
                recommended_action = "Fix quality issues or quarantine"
        
        # Save periodically
        if self.total_audits % 100 == 0:
            self._save_registry()
        
        return DataAuditResult(
            passed=passed,
            score=score,
            issues=issues,
            warnings=warnings,
            freshness_days=freshness_result.get('age_days'),
            has_provenance=provenance_result['has_provenance'],
            conflicts_detected=conflict_result['conflicts'],
            duplicates_detected=1 if duplicate_result['is_duplicate'] else 0,
            recommended_action=recommended_action
        )
    
    def _check_freshness(self, metadata: Dict) -> Dict:
        """Check if data is fresh"""
        
        timestamp_str = metadata.get('timestamp') or metadata.get('created_at')
        
        if not timestamp_str:
            return {
                'issue': False,
                'warning': "No timestamp - cannot verify freshness",
                'age_days': None
            }
        
        try:
            timestamp = datetime.fromisoformat(timestamp_str)
            age = datetime.utcnow() - timestamp
            age_days = age.days
            
            if age_days > self.max_age_days:
                return {
                    'issue': True,
                    'warning': f"Data is {age_days} days old",
                    'age_days': age_days
                }
            
            return {
                'issue': False,
                'warning': None,
                'age_days': age_days
            }
        
        except Exception as e:
            return {
                'issue': False,
                'warning': f"Invalid timestamp format: {e}",
                'age_days': None
            }
    
    def _check_provenance(self, metadata: Dict) -> Dict:
        """Check if data has provenance"""
        
        source = metadata.get('source')
        author = metadata.get('author')
        lineage = metadata.get('lineage')
        
        has_provenance = bool(source or author or lineage)
        
        provenance = {}
        if source:
            provenance['source'] = source
        if author:
            provenance['author'] = author
        if lineage:
            provenance['lineage'] = lineage
        
        return {
            'has_provenance': has_provenance,
            'provenance': provenance
        }
    
    def _check_format(self, content: str, metadata: Dict) -> Dict:
        """Validate format"""
        
        # Basic validation
        if not content or len(content.strip()) == 0:
            return {
                'valid': False,
                'reason': "Empty content"
            }
        
        # Check minimum length
        if len(content) < 10:
            return {
                'valid': False,
                'reason': "Content too short"
            }
        
        # Check for binary data in text
        try:
            content.encode('utf-8')
        except:
            return {
                'valid': False,
                'reason': "Invalid text encoding"
            }
        
        return {
            'valid': True,
            'reason': None
        }
    
    def _hash_content(self, content: str) -> str:
        """Hash content for deduplication"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def _check_duplicates(self, content: str) -> Dict:
        """Check for duplicate content"""
        
        content_hash = self._hash_content(content)
        is_duplicate = content_hash in self.content_hashes
        
        return {
            'is_duplicate': is_duplicate,
            'hash': content_hash
        }
    
    async def _check_conflicts(
        self,
        content: str,
        existing_data: Optional[List[Dict]]
    ) -> Dict:
        """Check for conflicts with existing data"""
        
        if not existing_data:
            return {'conflicts': 0}
        
        # Simple conflict detection based on contradictory keywords
        content_lower = content.lower()
        
        conflicts = 0
        
        for existing in existing_data:
            existing_content = existing.get('content', '').lower()
            
            # Check for obvious contradictions
            if self._has_contradiction(content_lower, existing_content):
                conflicts += 1
        
        return {'conflicts': conflicts}
    
    def _has_contradiction(self, text1: str, text2: str) -> bool:
        """Simple contradiction detection"""
        
        # Look for opposite statements
        contradiction_pairs = [
            ("is true", "is false"),
            ("correct", "incorrect"),
            ("valid", "invalid"),
            ("works", "doesn't work"),
            ("supported", "not supported")
        ]
        
        for pos, neg in contradiction_pairs:
            if (pos in text1 and neg in text2) or (neg in text1 and pos in text2):
                return True
        
        return False
    
    def _assess_quality(self, content: str, metadata: Dict) -> Dict:
        """Assess overall quality"""
        
        score = 1.0
        
        # Length check
        if len(content) < 50:
            score -= 0.2
        
        # Capitalization (basic quality indicator)
        if content[0].islower():
            score -= 0.1
        
        # Has metadata
        if not metadata:
            score -= 0.2
        
        # Has structure (sentences, paragraphs)
        if '.' not in content:
            score -= 0.1
        
        return {'score': max(0.0, score)}
    
    def get_stats(self) -> Dict:
        """Get pipeline statistics"""
        
        pass_rate = self.passed_audits / max(1, self.total_audits)
        
        return {
            'total_audits': self.total_audits,
            'passed': self.passed_audits,
            'failed': self.failed_audits,
            'pass_rate': pass_rate,
            'quarantined': self.quarantined_items,
            'unique_content_pieces': len(self.content_hashes),
            'provenance_tracked': len(self.provenance_registry)
        }


# Global pipeline
data_hygiene_pipeline = DataHygienePipeline()
