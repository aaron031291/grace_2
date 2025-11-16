"""
Metadata Standards and Discipline

Standardizes metadata keys across all domains for collective intelligence.

Benefits:
- Filtered RAG queries (e.g., "only network-domain insights with confidence >0.8 in last 24h")
- Consistent data structure across all knowledge sources
- Queryable by any dimension (domain, priority, confidence, time, tags)
- Easier correlation and pattern detection

Standard Keys:
- domain_id: Source domain
- intent_id: Related intent (if applicable)
- priority: low, normal, high, critical
- confidence: 0.0-1.0 confidence score
- tags: List of categorization tags
- timestamp: ISO 8601 timestamp
- source: Source identifier
- category: Knowledge category
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class Priority(Enum):
    """Standard priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class MetadataSchema:
    """
    Standard metadata schema enforcer
    
    Ensures all metadata follows the same structure
    """
    
    # Required keys for all metadata
    REQUIRED_KEYS = ["domain_id", "timestamp"]
    
    # Optional keys with defaults
    OPTIONAL_KEYS = {
        "priority": Priority.NORMAL.value,
        "confidence": 0.8,
        "tags": [],
        "intent_id": None,
        "source": "unknown",
        "category": "general"
    }
    
    # Type validation
    TYPE_RULES = {
        "domain_id": str,
        "timestamp": str,
        "priority": str,
        "confidence": (int, float),
        "tags": list,
        "intent_id": (str, type(None)),
        "source": str,
        "category": str
    }
    
    @staticmethod
    def enforce(metadata: Dict[str, Any], domain_id: str) -> Dict[str, Any]:
        """
        Enforce metadata standards
        
        Args:
            metadata: Raw metadata dictionary
            domain_id: Domain providing the metadata
            
        Returns:
            Standardized metadata dictionary
        """
        standardized = {}
        
        # Add required keys
        standardized["domain_id"] = metadata.get("domain_id", domain_id)
        standardized["timestamp"] = metadata.get("timestamp", datetime.utcnow().isoformat())
        
        # Add optional keys with defaults
        for key, default in MetadataSchema.OPTIONAL_KEYS.items():
            if key in metadata:
                standardized[key] = metadata[key]
            else:
                standardized[key] = default
        
        # Validate and normalize priority
        if isinstance(standardized["priority"], str):
            try:
                Priority(standardized["priority"].lower())
                standardized["priority"] = standardized["priority"].lower()
            except ValueError:
                logger.warning(f"Invalid priority '{standardized['priority']}', using 'normal'")
                standardized["priority"] = Priority.NORMAL.value
        
        # Validate confidence
        if not (0.0 <= standardized["confidence"] <= 1.0):
            logger.warning(f"Invalid confidence {standardized['confidence']}, clamping to [0,1]")
            standardized["confidence"] = max(0.0, min(1.0, standardized["confidence"]))
        
        # Ensure tags is a list
        if not isinstance(standardized["tags"], list):
            standardized["tags"] = [str(standardized["tags"])]
        
        # Add any extra metadata not in standard schema
        for key, value in metadata.items():
            if key not in standardized:
                standardized[key] = value
        
        return standardized
    
    @staticmethod
    def validate(metadata: Dict[str, Any]) -> bool:
        """
        Validate metadata complies with schema
        
        Returns:
            True if valid, False otherwise
        """
        # Check required keys
        for key in MetadataSchema.REQUIRED_KEYS:
            if key not in metadata:
                logger.error(f"Missing required metadata key: {key}")
                return False
        
        # Check types
        for key, expected_type in MetadataSchema.TYPE_RULES.items():
            if key in metadata:
                if not isinstance(metadata[key], expected_type):
                    logger.error(f"Invalid type for {key}: expected {expected_type}, got {type(metadata[key])}")
                    return False
        
        return True


class MetadataBuilder:
    """
    Builder for creating standardized metadata
    
    Usage:
        metadata = (MetadataBuilder(domain_id="network")
            .priority(Priority.HIGH)
            .confidence(0.95)
            .tags(["incident", "resolved"])
            .source("network_monitor")
            .build())
    """
    
    def __init__(self, domain_id: str):
        self._metadata = {
            "domain_id": domain_id,
            "timestamp": datetime.utcnow().isoformat(),
            "priority": Priority.NORMAL.value,
            "confidence": 0.8,
            "tags": [],
            "source": "unknown",
            "category": "general"
        }
    
    def priority(self, priority: Priority) -> 'MetadataBuilder':
        """Set priority"""
        self._metadata["priority"] = priority.value if isinstance(priority, Priority) else priority
        return self
    
    def confidence(self, confidence: float) -> 'MetadataBuilder':
        """Set confidence (0.0-1.0)"""
        self._metadata["confidence"] = max(0.0, min(1.0, confidence))
        return self
    
    def tags(self, tags: List[str]) -> 'MetadataBuilder':
        """Set tags"""
        self._metadata["tags"] = tags
        return self
    
    def add_tag(self, tag: str) -> 'MetadataBuilder':
        """Add a single tag"""
        if tag not in self._metadata["tags"]:
            self._metadata["tags"].append(tag)
        return self
    
    def source(self, source: str) -> 'MetadataBuilder':
        """Set source"""
        self._metadata["source"] = source
        return self
    
    def category(self, category: str) -> 'MetadataBuilder':
        """Set category"""
        self._metadata["category"] = category
        return self
    
    def intent(self, intent_id: str) -> 'MetadataBuilder':
        """Set intent ID"""
        self._metadata["intent_id"] = intent_id
        return self
    
    def custom(self, key: str, value: Any) -> 'MetadataBuilder':
        """Add custom metadata field"""
        self._metadata[key] = value
        return self
    
    def build(self) -> Dict[str, Any]:
        """Build and return metadata"""
        return self._metadata.copy()


class MetadataFilter:
    """
    Query filter builder for metadata-based searches
    
    Usage:
        filter = (MetadataFilter()
            .domain("network")
            .priority_min(Priority.HIGH)
            .confidence_min(0.8)
            .time_window_hours(24)
            .has_tag("incident")
            .build())
        
        results = await rag_service.retrieve(
            query="network issues",
            filters=filter
        )
    """
    
    def __init__(self):
        self._filters = {}
    
    def domain(self, domain_id: str) -> 'MetadataFilter':
        """Filter by domain"""
        self._filters["domain_id"] = domain_id
        return self
    
    def priority_min(self, priority: Priority) -> 'MetadataFilter':
        """Filter by minimum priority"""
        priorities = [p.value for p in Priority]
        min_idx = priorities.index(priority.value)
        self._filters["priority__in"] = priorities[min_idx:]
        return self
    
    def confidence_min(self, confidence: float) -> 'MetadataFilter':
        """Filter by minimum confidence"""
        self._filters["confidence__gte"] = confidence
        return self
    
    def has_tag(self, tag: str) -> 'MetadataFilter':
        """Filter by tag presence"""
        if "tags__contains" not in self._filters:
            self._filters["tags__contains"] = []
        self._filters["tags__contains"].append(tag)
        return self
    
    def time_window_hours(self, hours: int) -> 'MetadataFilter':
        """Filter by time window"""
        from datetime import timedelta
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        self._filters["timestamp__gte"] = cutoff.isoformat()
        return self
    
    def source(self, source: str) -> 'MetadataFilter':
        """Filter by source"""
        self._filters["source"] = source
        return self
    
    def category(self, category: str) -> 'MetadataFilter':
        """Filter by category"""
        self._filters["category"] = category
        return self
    
    def build(self) -> Dict[str, Any]:
        """Build and return filter"""
        return self._filters.copy()


# Helper functions for domains

def create_artifact_metadata(
    domain_id: str,
    artifact_type: str,
    priority: Priority = Priority.NORMAL,
    confidence: float = 0.8,
    tags: Optional[List[str]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Create metadata for domain artifacts
    
    Usage:
        metadata = create_artifact_metadata(
            domain_id="network",
            artifact_type="incident_report",
            priority=Priority.HIGH,
            confidence=0.95,
            tags=["resolved", "network"],
            incident_id="INC-001"
        )
    """
    builder = (MetadataBuilder(domain_id)
        .priority(priority)
        .confidence(confidence)
        .tags(tags or [])
        .source(f"{domain_id}_{artifact_type}")
        .category(artifact_type))
    
    for key, value in kwargs.items():
        builder.custom(key, value)
    
    return builder.build()


def create_knowledge_metadata(
    domain,
    knowledge_type: str,
    confidence: float = 0.8,
    tags: Optional[List[str]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Create metadata for knowledge contributions
    
    Usage:
        metadata = create_knowledge_metadata(
            domain_id="ml",
            knowledge_type="model_insight",
            confidence=0.92,
            tags=["training", "optimization"],
            model_id="model_v2"
        )
    """
    return create_artifact_metadata(
        domain_id=domain_id,
        artifact_type=knowledge_type,
        priority=Priority.NORMAL,
        confidence=confidence,
        tags=(tags or []) + ["knowledge"],
        **kwargs
    )


def create_insight_metadata(
    domain_id: str,
    insight_type: str,
    priority: Priority = Priority.NORMAL,
    confidence: float = 0.75,
    **kwargs
) -> Dict[str, Any]:
    """
    Create metadata for insights
    
    Usage:
        metadata = create_insight_metadata(
            domain_id="temporal",
            insight_type="pattern_detected",
            priority=Priority.HIGH,
            confidence=0.88,
            pattern_id="PATTERN-123"
        )
    """
    return create_artifact_metadata(
        domain_id=domain_id,
        artifact_type=insight_type,
        priority=priority,
        confidence=confidence,
        tags=["insight", insight_type],
        **kwargs
    )


# Query helpers

def query_by_domain(
    domain_id: str,
    confidence_min: float = 0.7,
    hours: int = 168  # 1 week
) -> Dict[str, Any]:
    """
    Build filter for domain-specific queries
    
    Usage:
        filter = query_by_domain("network", confidence_min=0.8, hours=24)
        results = await rag_service.retrieve(query="issues", filters=filter)
    """
    return (MetadataFilter()
        .domain(domain_id)
        .confidence_min(confidence_min)
        .time_window_hours(hours)
        .build())


def query_high_confidence(
    confidence_min: float = 0.9,
    priority_min: Priority = Priority.HIGH
) -> Dict[str, Any]:
    """
    Build filter for high-confidence, high-priority items
    
    Usage:
        filter = query_high_confidence()
        results = await rag_service.retrieve(query="critical issues", filters=filter)
    """
    return (MetadataFilter()
        .confidence_min(confidence_min)
        .priority_min(priority_min)
        .build())


def query_recent_insights(
    hours: int = 24,
    tags: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Build filter for recent insights
    
    Usage:
        filter = query_recent_insights(hours=24, tags=["resolved"])
        results = await rag_service.retrieve(query="recent fixes", filters=filter)
    """
    builder = MetadataFilter().time_window_hours(hours).category("insight")
    
    if tags:
        for tag in tags:
            builder.has_tag(tag)
    
    return builder.build()


# Validation and enforcement

def validate_and_enforce(metadata: Dict[str, Any], domain_id: str) -> Dict[str, Any]:
    """
    Validate and enforce metadata standards
    
    Usage in domains when publishing artifacts:
        metadata = validate_and_enforce(raw_metadata, "network")
        await shared_memory.contribute(domain_id, key, value, metadata=metadata)
    """
    standardized = MetadataSchema.enforce(metadata, domain_id)
    
    if not MetadataSchema.validate(standardized):
        logger.warning(f"Metadata validation failed for domain {domain_id}, using defaults")
        # Still return standardized version with defaults
    
    return standardized