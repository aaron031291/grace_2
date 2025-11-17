"""
World Model Summary Pipeline

Promotes domain knowledge to first-class curated knowledge in the world model.

When domains complete missions, solve incidents, or generate insights:
1. They publish structured summaries
2. Pipeline auto-ingests into vector store (raw embeddings)
3. Pipeline adds to grace_world_model (curated with confidence/tags)

This creates a two-tier knowledge system:
- Raw embeddings: Full context for semantic search
- World model: Curated facts with metadata for structured queries
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class DomainSummary:
    """Structured summary from a domain"""
    domain_id: str
    summary_type: str  # 'mission_complete', 'incident_resolved', 'insight_generated'
    title: str
    description: str
    cause: Optional[str] = None
    fix: Optional[str] = None
    confidence: float = 0.8
    tags: List[str] = None
    metadata: Dict[str, Any] = None
    priority: str = "normal"  # low, normal, high, critical
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.metadata is None:
            self.metadata = {}


class WorldModelSummaryPipeline:
    """
    Pipeline for ingesting domain summaries into world model
    
    Listens for domain events and auto-ingests structured knowledge
    """
    
    def __init__(self):
        self._initialized = False
        self.summaries_processed = 0
        self.failed_ingestions = 0
    
    async def initialize(self):
        """Initialize pipeline and subscribe to domain events"""
        if self._initialized:
            return
        
        logger.info("[SUMMARY-PIPELINE] Initializing world model summary pipeline")
        
        # Subscribe to domain events
        try:
            from backend.domains import domain_event_bus
            
            # Subscribe to relevant events
            domain_event_bus.subscribe("mission.completed", self._handle_mission_completed)
            domain_event_bus.subscribe("incident.resolved", self._handle_incident_resolved)
            domain_event_bus.subscribe("insight.generated", self._handle_insight_generated)
            domain_event_bus.subscribe("knowledge.discovered", self._handle_knowledge_discovered)
            
            logger.info("[SUMMARY-PIPELINE] Subscribed to domain events")
        except Exception as e:
            logger.warning(f"[SUMMARY-PIPELINE] Could not subscribe to domain events: {e}")
        
        self._initialized = True
        logger.info("[SUMMARY-PIPELINE] Pipeline ready")
    
    async def ingest_summary(self, summary: DomainSummary) -> Dict[str, Any]:
        """
        Ingest a domain summary into both vector store and world model
        
        Args:
            summary: Structured domain summary
            
        Returns:
            {
                "embedding_id": str,
                "knowledge_id": str,
                "indexed": bool,
                "success": bool
            }
        """
        try:
            # Build content text
            content_parts = [
                f"Domain: {summary.domain_id}",
                f"Type: {summary.summary_type}",
                f"Title: {summary.title}",
                f"Description: {summary.description}"
            ]
            
            if summary.cause:
                content_parts.append(f"Cause: {summary.cause}")
            if summary.fix:
                content_parts.append(f"Fix: {summary.fix}")
            
            content = "\n".join(content_parts)
            
            # Step 1: Ingest into vector store (raw embeddings)
            from backend.services.vector_store import vector_store
            
            vector_result = await vector_store.add_text(
                content=content,
                source=f"{summary.domain_id}/{summary.summary_type}",
                metadata={
                    "domain_id": summary.domain_id,
                    "summary_type": summary.summary_type,
                    "title": summary.title,
                    "confidence": summary.confidence,
                    "priority": summary.priority,
                    "tags": summary.tags,
                    "timestamp": datetime.utcnow().isoformat(),
                    **summary.metadata
                },
                source_type="domain_summary",
                source_id=f"{summary.domain_id}_{summary.summary_type}_{datetime.utcnow().timestamp()}"
            )
            
            # Step 2: Add to world model (curated knowledge)
            from backend.world_model import grace_world_model
            
            knowledge_id = await grace_world_model.add_knowledge(
                category='domain',
                content=content,
                source=f"{summary.domain_id}_summary",
                confidence=summary.confidence,
                tags=summary.tags + [summary.domain_id, summary.summary_type],
                metadata={
                    "domain_id": summary.domain_id,
                    "summary_type": summary.summary_type,
                    "title": summary.title,
                    "priority": summary.priority,
                    "cause": summary.cause,
                    "fix": summary.fix,
                    "embedding_id": vector_result.get("embedding_id"),
                    **summary.metadata
                }
            )
            
            self.summaries_processed += 1
            
            logger.info(
                f"[SUMMARY-PIPELINE] Ingested summary from {summary.domain_id}: "
                f"{summary.title} (confidence: {summary.confidence})"
            )
            
            return {
                "embedding_id": vector_result.get("embedding_id"),
                "knowledge_id": knowledge_id,
                "indexed": vector_result.get("indexed", False),
                "success": True,
                "domain_id": summary.domain_id,
                "summary_type": summary.summary_type
            }
            
        except Exception as e:
            self.failed_ingestions += 1
            logger.error(f"[SUMMARY-PIPELINE] Failed to ingest summary: {e}")
            
            return {
                "success": False,
                "error": str(e),
                "domain_id": summary.domain_id,
                "summary_type": summary.summary_type
            }
    
    async def _handle_mission_completed(self, event):
        """Handle mission completed event"""
        try:
            data = event.data if hasattr(event, 'data') else event
            
            summary = DomainSummary(
                domain_id=data.get("domain_id", "unknown"),
                summary_type="mission_complete",
                title=data.get("mission_title", "Mission Completed"),
                description=data.get("outcome", "Mission completed successfully"),
                confidence=data.get("success_confidence", 0.9),
                tags=["mission", "completed"],
                metadata={
                    "mission_id": data.get("mission_id"),
                    "duration_seconds": data.get("duration_seconds"),
                    "steps_completed": data.get("steps_completed")
                }
            )
            
            await self.ingest_summary(summary)
            
        except Exception as e:
            logger.error(f"[SUMMARY-PIPELINE] Error handling mission completed: {e}")
    
    async def _handle_incident_resolved(self, event):
        """Handle incident resolved event"""
        try:
            data = event.data if hasattr(event, 'data') else event
            
            summary = DomainSummary(
                domain_id=data.get("domain_id", "unknown"),
                summary_type="incident_resolved",
                title=data.get("incident_title", "Incident Resolved"),
                description=data.get("resolution_summary", "Incident was resolved"),
                cause=data.get("root_cause"),
                fix=data.get("fix_applied"),
                confidence=data.get("resolution_confidence", 0.85),
                tags=["incident", "resolved", "fix"],
                priority=data.get("severity", "normal"),
                metadata={
                    "incident_id": data.get("incident_id"),
                    "resolution_time_seconds": data.get("resolution_time"),
                    "auto_remediated": data.get("auto_remediated", False)
                }
            )
            
            await self.ingest_summary(summary)
            
        except Exception as e:
            logger.error(f"[SUMMARY-PIPELINE] Error handling incident resolved: {e}")
    
    async def _handle_insight_generated(self, event):
        """Handle insight generated event"""
        try:
            data = event.data if hasattr(event, 'data') else event
            
            summary = DomainSummary(
                domain_id=data.get("domain_id", "unknown"),
                summary_type="insight_generated",
                title=data.get("insight_title", "New Insight"),
                description=data.get("insight_text", "Insight generated from analysis"),
                confidence=data.get("confidence", 0.75),
                tags=["insight", "analysis"] + data.get("tags", []),
                metadata={
                    "insight_id": data.get("insight_id"),
                    "analysis_type": data.get("analysis_type"),
                    "data_sources": data.get("data_sources", [])
                }
            )
            
            await self.ingest_summary(summary)
            
        except Exception as e:
            logger.error(f"[SUMMARY-PIPELINE] Error handling insight generated: {e}")
    
    async def _handle_knowledge_discovered(self, event):
        """Handle knowledge discovered event"""
        try:
            data = event.data if hasattr(event, 'data') else event
            
            summary = DomainSummary(
                domain_id=data.get("domain_id", "unknown"),
                summary_type="knowledge_discovered",
                title=data.get("knowledge_title", "Knowledge Discovered"),
                description=data.get("knowledge_description", "New knowledge acquired"),
                confidence=data.get("confidence", 0.8),
                tags=["knowledge", "discovery"] + data.get("tags", []),
                metadata={
                    "knowledge_source": data.get("source"),
                    "discovery_method": data.get("method")
                }
            )
            
            await self.ingest_summary(summary)
            
        except Exception as e:
            logger.error(f"[SUMMARY-PIPELINE] Error handling knowledge discovered: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get pipeline statistics"""
        return {
            "initialized": self._initialized,
            "summaries_processed": self.summaries_processed,
            "failed_ingestions": self.failed_ingestions,
            "success_rate": (
                (self.summaries_processed / (self.summaries_processed + self.failed_ingestions))
                if (self.summaries_processed + self.failed_ingestions) > 0
                else 1.0
            )
        }
    
    async def query_domain_summaries(
        self,
        domain_id: Optional[str] = None,
        summary_type: Optional[str] = None,
        min_confidence: float = 0.0,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Query summaries from the world model
        
        Args:
            domain_id: Filter by domain
            summary_type: Filter by type
            min_confidence: Minimum confidence threshold
            limit: Maximum results
            
        Returns:
            List of matching summaries
        """
        from backend.world_model import grace_world_model
        
        # Build query
        query_parts = []
        if domain_id:
            query_parts.append(f"domain:{domain_id}")
        if summary_type:
            query_parts.append(f"type:{summary_type}")
        
        query_text = " ".join(query_parts) if query_parts else "domain summaries"
        
        # Query world model
        results = await grace_world_model.query(
            query=query_text,
            category='domain',
            min_confidence=min_confidence,
            top_k=limit
        )
        
        return [r.to_dict() for r in results]


# Global singleton
world_model_summary_pipeline = WorldModelSummaryPipeline()


# Convenience functions for domains to publish summaries
async def publish_mission_summary(
    domain_id: str,
    mission_title: str,
    outcome: str,
    mission_id: str,
    confidence: float = 0.9,
    **kwargs
) -> Dict[str, Any]:
    """Publish a mission completion summary"""
    summary = DomainSummary(
        domain_id=domain_id,
        summary_type="mission_complete",
        title=mission_title,
        description=outcome,
        confidence=confidence,
        tags=["mission", "completed"],
        metadata={"mission_id": mission_id, **kwargs}
    )
    
    return await world_model_summary_pipeline.ingest_summary(summary)


async def publish_incident_summary(
    domain_id: str,
    incident_title: str,
    resolution_summary: str,
    root_cause: str,
    fix_applied: str,
    confidence: float = 0.85,
    **kwargs
) -> Dict[str, Any]:
    """Publish an incident resolution summary"""
    summary = DomainSummary(
        domain_id=domain_id,
        summary_type="incident_resolved",
        title=incident_title,
        description=resolution_summary,
        cause=root_cause,
        fix=fix_applied,
        confidence=confidence,
        tags=["incident", "resolved"],
        metadata=kwargs
    )
    
    return await world_model_summary_pipeline.ingest_summary(summary)


async def publish_insight_summary(
    domain_id: str,
    insight_title: str,
    insight_text: str,
    confidence: float = 0.75,
    tags: Optional[List[str]] = None,
    **kwargs
) -> Dict[str, Any]:
    """Publish an insight summary"""
    summary = DomainSummary(
        domain_id=domain_id,
        summary_type="insight_generated",
        title=insight_title,
        description=insight_text,
        confidence=confidence,
        tags=["insight"] + (tags or []),
        metadata=kwargs
    )
    
    return await world_model_summary_pipeline.ingest_summary(summary)