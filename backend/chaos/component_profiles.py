"""
Component Profiles for Chaos Engineering
Catalog every component with domain-specific stress patterns and guardrails

Components:
- Backend APIs (OWASP tests)
- Database systems (schema mutations, load spikes)
- RAG pipeline (malformed queries, load)
- HTM detectors (anomaly injection)
- Remote access (auth failures, rate limits)
- Message bus (queue overflow)
"""

import logging
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class ComponentType(str, Enum):
    """Types of components"""
    API_ENDPOINT = "api_endpoint"
    DATABASE = "database"
    MESSAGE_QUEUE = "message_queue"
    RAG_PIPELINE = "rag_pipeline"
    HTM_DETECTOR = "htm_detector"
    REMOTE_ACCESS = "remote_access"
    KERNEL = "kernel"
    AGENT = "agent"
    MODEL = "model"


class StressPattern(str, Enum):
    """Standard stress patterns"""
    
    # API patterns (OWASP-inspired)
    SQL_INJECTION = "sql_injection"
    XSS_ATTACK = "xss_attack"
    AUTH_BYPASS = "auth_bypass"
    RATE_LIMIT_BREACH = "rate_limit_breach"
    PAYLOAD_OVERFLOW = "payload_overflow"
    
    # Load patterns
    BURST_TRAFFIC = "burst_traffic"
    SLOWLORIS = "slowloris"
    CONNECTION_EXHAUSTION = "connection_exhaustion"
    MEMORY_LEAK = "memory_leak"
    
    # Data patterns
    SCHEMA_MUTATION = "schema_mutation"
    MALFORMED_DATA = "malformed_data"
    NULL_INJECTION = "null_injection"
    TYPE_CONFUSION = "type_confusion"
    
    # Configuration patterns
    CONFIG_DRIFT = "config_drift"
    MISSING_SECRETS = "missing_secrets"
    FEATURE_FLAG_CHAOS = "feature_flag_chaos"
    
    # Resource patterns
    DISK_FULL = "disk_full"
    NETWORK_PARTITION = "network_partition"
    DNS_FAILURE = "dns_failure"
    
    # Circuit breaker tests
    CASCADING_FAILURE = "cascading_failure"
    TIMEOUT_STORM = "timeout_storm"
    RETRY_EXHAUSTION = "retry_exhaustion"


@dataclass
class Guardrail:
    """Expected guardrail that should block chaos"""
    
    guardrail_type: str  # 'rate_limit', 'auth', 'circuit_breaker', etc.
    expected_behavior: str  # What should happen
    threshold: Optional[float] = None
    timeout_ms: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'guardrail_type': self.guardrail_type,
            'expected_behavior': self.expected_behavior,
            'threshold': self.threshold,
            'timeout_ms': self.timeout_ms
        }


@dataclass
class ComponentProfile:
    """Profile for a component with stress patterns and guardrails"""
    
    component_id: str
    component_name: str
    component_type: ComponentType
    description: str
    
    # Stress patterns this component should survive
    stress_patterns: List[StressPattern] = field(default_factory=list)
    
    # Expected guardrails
    guardrails: List[Guardrail] = field(default_factory=list)
    
    # Component-specific metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Resilience score (updated by chaos tests)
    resilience_score: float = 0.0  # 0.0 - 1.0
    last_tested: Optional[str] = None
    test_history: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'component_id': self.component_id,
            'component_name': self.component_name,
            'component_type': self.component_type.value,
            'description': self.description,
            'stress_patterns': [p.value for p in self.stress_patterns],
            'guardrails': [g.to_dict() for g in self.guardrails],
            'metadata': self.metadata,
            'resilience_score': self.resilience_score,
            'last_tested': self.last_tested,
            'test_count': len(self.test_history)
        }


class ComponentProfileRegistry:
    """
    Registry of all component profiles
    Catalogs every microservice/component with stress patterns
    """
    
    def __init__(self):
        self.profiles: Dict[str, ComponentProfile] = {}
        self._initialize_default_profiles()
    
    def _initialize_default_profiles(self):
        """Create default component profiles"""
        
        # API Endpoints
        self.register_profile(ComponentProfile(
            component_id='backend_api',
            component_name='Grace Backend API',
            component_type=ComponentType.API_ENDPOINT,
            description='Main FastAPI backend',
            stress_patterns=[
                StressPattern.SQL_INJECTION,
                StressPattern.XSS_ATTACK,
                StressPattern.AUTH_BYPASS,
                StressPattern.RATE_LIMIT_BREACH,
                StressPattern.PAYLOAD_OVERFLOW,
                StressPattern.BURST_TRAFFIC,
                StressPattern.SLOWLORIS
            ],
            guardrails=[
                Guardrail('rate_limit', 'Block after 100 req/min', threshold=100.0),
                Guardrail('auth', 'Require valid token', threshold=None),
                Guardrail('payload_size', 'Reject > 10MB', threshold=10.0),
                Guardrail('timeout', 'Timeout after 30s', timeout_ms=30000)
            ],
            metadata={'port': 8000, 'framework': 'fastapi'}
        ))
        
        # Database
        self.register_profile(ComponentProfile(
            component_id='grace_database',
            component_name='Grace Database',
            component_type=ComponentType.DATABASE,
            description='SQLite database',
            stress_patterns=[
                StressPattern.SQL_INJECTION,
                StressPattern.SCHEMA_MUTATION,
                StressPattern.CONNECTION_EXHAUSTION,
                StressPattern.DISK_FULL,
                StressPattern.MALFORMED_DATA,
                StressPattern.NULL_INJECTION
            ],
            guardrails=[
                Guardrail('connection_pool', 'Max 100 connections', threshold=100.0),
                Guardrail('query_timeout', 'Timeout after 10s', timeout_ms=10000),
                Guardrail('prepared_statements', 'Use parameterized queries')
            ],
            metadata={'type': 'sqlite', 'path': 'grace.db'}
        ))
        
        # RAG Pipeline
        self.register_profile(ComponentProfile(
            component_id='rag_pipeline',
            component_name='RAG Pipeline',
            component_type=ComponentType.RAG_PIPELINE,
            description='Retrieval-Augmented Generation',
            stress_patterns=[
                StressPattern.MALFORMED_DATA,
                StressPattern.BURST_TRAFFIC,
                StressPattern.MEMORY_LEAK,
                StressPattern.NULL_INJECTION,
                StressPattern.TYPE_CONFUSION
            ],
            guardrails=[
                Guardrail('embedding_validation', 'Validate vector dimensions'),
                Guardrail('query_sanitization', 'Sanitize user queries'),
                Guardrail('result_limit', 'Max 100 results', threshold=100.0)
            ],
            metadata={'vector_store': 'chromadb', 'embedding_model': 'sentence-transformers'}
        ))
        
        # HTM Detector
        self.register_profile(ComponentProfile(
            component_id='htm_detector',
            component_name='HTM Anomaly Detector',
            component_type=ComponentType.HTM_DETECTOR,
            description='Hierarchical Temporal Memory anomaly detection',
            stress_patterns=[
                StressPattern.MALFORMED_DATA,
                StressPattern.BURST_TRAFFIC,
                StressPattern.NULL_INJECTION,
                StressPattern.TYPE_CONFUSION
            ],
            guardrails=[
                Guardrail('input_validation', 'Validate metric values'),
                Guardrail('anomaly_threshold', 'Score clamped 0-1', threshold=1.0)
            ],
            metadata={'detectors': 'multiple', 'metrics': ['response_time', 'error_rate']}
        ))
        
        # Remote Access
        self.register_profile(ComponentProfile(
            component_id='remote_access',
            component_name='Remote Access System',
            component_type=ComponentType.REMOTE_ACCESS,
            description='Firefox agent and remote computer access',
            stress_patterns=[
                StressPattern.AUTH_BYPASS,
                StressPattern.RATE_LIMIT_BREACH,
                StressPattern.CONNECTION_EXHAUSTION,
                StressPattern.DNS_FAILURE,
                StressPattern.MISSING_SECRETS
            ],
            guardrails=[
                Guardrail('auth', 'Require valid credentials'),
                Guardrail('domain_whitelist', 'Block non-whitelisted domains'),
                Guardrail('https_only', 'Reject HTTP requests'),
                Guardrail('rate_limit', 'Max 10 req/min', threshold=10.0)
            ],
            metadata={'firefox_enabled': True, 'domains': 10}
        ))
        
        # Message Bus
        self.register_profile(ComponentProfile(
            component_id='message_bus',
            component_name='Message Bus',
            component_type=ComponentType.MESSAGE_QUEUE,
            description='Event streaming and pub/sub',
            stress_patterns=[
                StressPattern.BURST_TRAFFIC,
                StressPattern.MEMORY_LEAK,
                StressPattern.CONNECTION_EXHAUSTION,
                StressPattern.MALFORMED_DATA
            ],
            guardrails=[
                Guardrail('queue_limit', 'Max 10000 messages', threshold=10000.0),
                Guardrail('message_size', 'Max 1MB per message', threshold=1.0),
                Guardrail('subscription_limit', 'Max 1000 subscribers', threshold=1000.0)
            ],
            metadata={'backend': 'in-memory', 'persistence': False}
        ))
        
        # Guardian Kernel
        self.register_profile(ComponentProfile(
            component_id='guardian_kernel',
            component_name='Guardian Kernel',
            component_type=ComponentType.KERNEL,
            description='Boot orchestration and network healing',
            stress_patterns=[
                StressPattern.NETWORK_PARTITION,
                StressPattern.DNS_FAILURE,
                StressPattern.CONNECTION_EXHAUSTION,
                StressPattern.CONFIG_DRIFT,
                StressPattern.CASCADING_FAILURE
            ],
            guardrails=[
                Guardrail('network_healing', 'Auto-heal within 30s', timeout_ms=30000),
                Guardrail('boot_validation', 'Validate each chunk'),
                Guardrail('delegation', 'Delegate to self-healing')
            ],
            metadata={'priority': 0, 'critical': True}
        ))
        
        # Learning Mission Launcher
        self.register_profile(ComponentProfile(
            component_id='learning_mission_launcher',
            component_name='Learning Mission Launcher',
            component_type=ComponentType.AGENT,
            description='Autonomous learning mission execution',
            stress_patterns=[
                StressPattern.BURST_TRAFFIC,
                StressPattern.MALFORMED_DATA,
                StressPattern.MISSING_SECRETS,
                StressPattern.TIMEOUT_STORM
            ],
            guardrails=[
                Guardrail('concurrent_limit', 'Max 3 concurrent missions', threshold=3.0),
                Guardrail('approval_required', 'Governance approval for high-risk'),
                Guardrail('rbac', 'Service account permissions')
            ],
            metadata={'service_account': 'learning_mission_service'}
        ))
        
        logger.info(f"[COMPONENT-PROFILES] Initialized {len(self.profiles)} component profiles")
    
    def register_profile(self, profile: ComponentProfile):
        """Register a component profile"""
        self.profiles[profile.component_id] = profile
        logger.debug(f"[COMPONENT-PROFILES] Registered: {profile.component_id}")
    
    def get_profile(self, component_id: str) -> Optional[ComponentProfile]:
        """Get component profile"""
        return self.profiles.get(component_id)
    
    def list_profiles(self, component_type: Optional[ComponentType] = None) -> List[ComponentProfile]:
        """List profiles, optionally filtered by type"""
        
        profiles = list(self.profiles.values())
        
        if component_type:
            profiles = [p for p in profiles if p.component_type == component_type]
        
        return profiles
    
    def get_by_resilience(self, ascending: bool = True) -> List[ComponentProfile]:
        """Get components sorted by resilience score"""
        profiles = list(self.profiles.values())
        profiles.sort(key=lambda p: p.resilience_score, reverse=not ascending)
        return profiles


# Global registry
component_registry = ComponentProfileRegistry()
