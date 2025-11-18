"""
Data Provenance Pipeline - Mandatory provenance for all responses
"""
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field
import hashlib
import logging

from backend.schemas import DataProvenance
from backend.logging.immutable_log import immutable_log

logger = logging.getLogger(__name__)

@dataclass
class ProvenanceMetadata:
    """Complete provenance metadata for any data"""
    source_id: str
    source_type: str  # "knowledge", "memory", "database", "external", "generated"
    source_url: Optional[str] = None
    retrieved_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    confidence: float = 0.0  # 0-1 confidence score
    verification_status: str = "unverified"  # "verified", "unverified", "failed"
    citation_text: str = ""
    lineage_chain: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

class ProvenancePipeline:
    """Mandatory provenance pipeline for all retrievals"""
    
    def __init__(self):
        self.provenance_cache = {}
        self.confidence_weights = {
            "source_reliability": 0.3,
            "content_freshness": 0.2,
            "verification_status": 0.25,
            "retrieval_accuracy": 0.15,
            "user_feedback": 0.1
        }
        self.stats = {
            "responses_processed": 0,
            "provenance_violations": 0,
            "confidence_scores_calculated": 0,
            "citations_generated": 0
        }
    
    async def enforce_provenance_requirement(self, response_data: Dict[str, Any], 
                                           source_documents: List[Dict] = None) -> Dict[str, Any]:
        """Enforce mandatory provenance on all responses"""
        logger.debug("🔍 Enforcing provenance requirements...")
        
        # Check if response already has provenance
        if not self._has_valid_provenance(response_data):
            logger.warning("⚠️ Response missing provenance - adding mandatory provenance")
            self.stats["provenance_violations"] += 1
            
            # Add mandatory provenance
            response_data = await self._add_mandatory_provenance(response_data, source_documents)
        
        # Ensure confidence scoring
        if "confidence_score" not in response_data:
            response_data["confidence_score"] = await self._calculate_confidence_score(
                response_data, source_documents or []
            )
            self.stats["confidence_scores_calculated"] += 1
        
        # Ensure citations
        if not response_data.get("citations"):
            response_data["citations"] = await self._generate_citations(
                response_data, source_documents or []
            )
            self.stats["citations_generated"] += 1
        
        # Add provenance metadata
        response_data["data_provenance"] = await self._build_provenance_metadata(
            response_data, source_documents or []
        )
        
        # Log provenance enforcement
        await immutable_log.append(
            actor="provenance_pipeline",
            action="provenance_enforced",
            resource="response",
            outcome="success",
            payload={
                "has_sources": len(source_documents or []) > 0,
                "confidence_score": response_data.get("confidence_score", 0),
                "citation_count": len(response_data.get("citations", [])),
                "provenance_count": len(response_data.get("data_provenance", []))
            }
        )
        
        self.stats["responses_processed"] += 1
        return response_data
    
    def _has_valid_provenance(self, response_data: Dict[str, Any]) -> bool:
        """Check if response has valid provenance"""
        required_fields = ["data_provenance", "confidence_score"]
        
        for field in required_fields:
            if field not in response_data:
                return False
        
        # Check if data_provenance is non-empty and valid
        provenance = response_data.get("data_provenance", [])
        if not provenance:
            return False
        
        # Validate provenance structure
        for prov in provenance:
            if not isinstance(prov, dict):
                return False
            required_prov_fields = ["source_type", "timestamp", "confidence", "verified"]
            if not all(field in prov for field in required_prov_fields):
                return False
        
        return True
    
    async def _add_mandatory_provenance(self, response_data: Dict[str, Any], 
                                      source_documents: List[Dict]) -> Dict[str, Any]:
        """Add mandatory provenance when missing"""
        
        # If no source documents, mark as generated content
        if not source_documents:
            response_data["data_provenance"] = [
                DataProvenance(
                    source_type="generated",
                    source_id="llm_generation",
                    timestamp=datetime.utcnow().isoformat(),
                    confidence=0.7,  # Default confidence for generated content
                    verified=False
                ).dict()
            ]
            response_data["confidence_score"] = 0.7
            response_data["citations"] = []
            return response_data
        
        # Build provenance from source documents
        provenance_list = []
        for i, doc in enumerate(source_documents):
            source_id = doc.get("source_id", f"doc_{i}")
            source_type = doc.get("source_type", "knowledge")
            
            provenance_list.append(
                DataProvenance(
                    source_type=source_type,
                    source_id=source_id,
                    timestamp=datetime.utcnow().isoformat(),
                    confidence=doc.get("confidence", 0.8),
                    verified=doc.get("verified", False)
                ).dict()
            )
        
        response_data["data_provenance"] = provenance_list
        return response_data
    
    async def _calculate_confidence_score(self, response_data: Dict[str, Any], 
                                        source_documents: List[Dict]) -> float:
        """Calculate comprehensive confidence score"""
        
        if not source_documents:
            # Generated content gets base confidence
            return 0.7
        
        confidence_factors = {}
        
        # Source reliability (30%)
        source_reliabilities = []
        for doc in source_documents:
            reliability = doc.get("trust_score", 0.5)
            if doc.get("verified", False):
                reliability += 0.2
            source_reliabilities.append(min(reliability, 1.0))
        
        confidence_factors["source_reliability"] = sum(source_reliabilities) / len(source_reliabilities)
        
        # Content freshness (20%)
        freshness_scores = []
        current_time = datetime.utcnow()
        
        for doc in source_documents:
            doc_time_str = doc.get("timestamp") or doc.get("created_at")
            if doc_time_str:
                try:
                    doc_time = datetime.fromisoformat(doc_time_str.replace('Z', '+00:00'))
                    age_days = (current_time - doc_time.replace(tzinfo=None)).days
                    
                    # Fresher content gets higher score
                    if age_days <= 7:
                        freshness = 1.0
                    elif age_days <= 30:
                        freshness = 0.8
                    elif age_days <= 90:
                        freshness = 0.6
                    elif age_days <= 365:
                        freshness = 0.4
                    else:
                        freshness = 0.2
                    
                    freshness_scores.append(freshness)
                except:
                    freshness_scores.append(0.5)  # Default for unparseable dates
            else:
                freshness_scores.append(0.5)  # Default for missing timestamps
        
        confidence_factors["content_freshness"] = sum(freshness_scores) / len(freshness_scores) if freshness_scores else 0.5
        
        # Verification status (25%)
        verified_count = sum(1 for doc in source_documents if doc.get("verified", False))
        confidence_factors["verification_status"] = verified_count / len(source_documents)
        
        # Retrieval accuracy (15%) - based on similarity scores
        similarity_scores = [doc.get("similarity_score", 0.7) for doc in source_documents]
        confidence_factors["retrieval_accuracy"] = sum(similarity_scores) / len(similarity_scores)
        
        # User feedback (10%) - placeholder for future implementation
        confidence_factors["user_feedback"] = 0.5  # Neutral default
        
        # Calculate weighted confidence score
        total_confidence = 0.0
        for factor, score in confidence_factors.items():
            weight = self.confidence_weights.get(factor, 0.0)
            total_confidence += score * weight
        
        # Ensure score is between 0 and 1
        final_confidence = max(0.0, min(1.0, total_confidence))
        
        logger.debug(f"Confidence calculation: {confidence_factors} -> {final_confidence:.3f}")
        return final_confidence
    
    async def _generate_citations(self, response_data: Dict[str, Any], 
                                source_documents: List[Dict]) -> List[Dict[str, Any]]:
        """Generate citations for response"""
        citations = []
        
        for i, doc in enumerate(source_documents):
            citation = {
                "id": f"cite_{i+1}",
                "source_id": doc.get("source_id", f"doc_{i}"),
                "title": doc.get("title", "Unknown Source"),
                "url": doc.get("url") or doc.get("source_url"),
                "author": doc.get("author"),
                "date": doc.get("timestamp") or doc.get("created_at"),
                "excerpt": doc.get("content", "")[:200] + "..." if len(doc.get("content", "")) > 200 else doc.get("content", ""),
                "confidence": doc.get("confidence", 0.8),
                "verified": doc.get("verified", False),
                "citation_format": self._format_citation(doc)
            }
            
            # Remove None values
            citation = {k: v for k, v in citation.items() if v is not None}
            citations.append(citation)
        
        return citations
    
    def _format_citation(self, doc: Dict[str, Any]) -> str:
        """Format citation in standard academic format"""
        title = doc.get("title", "Unknown Source")
        author = doc.get("author", "Unknown Author")
        url = doc.get("url") or doc.get("source_url", "")
        date = doc.get("timestamp") or doc.get("created_at", "")
        
        # Parse date
        if date:
            try:
                parsed_date = datetime.fromisoformat(date.replace('Z', '+00:00'))
                formatted_date = parsed_date.strftime("%Y-%m-%d")
            except:
                formatted_date = date[:10] if len(date) >= 10 else date
        else:
            formatted_date = "n.d."
        
        # Format citation
        citation = f"{author}. \"{title}.\" {formatted_date}."
        if url:
            citation += f" {url}"
        
        return citation
    
    async def _build_provenance_metadata(self, response_data: Dict[str, Any], 
                                       source_documents: List[Dict]) -> List[Dict[str, Any]]:
        """Build comprehensive provenance metadata"""
        provenance_list = []
        
        for doc in source_documents:
            provenance = {
                "source_type": doc.get("source_type", "knowledge"),
                "source_id": doc.get("source_id", "unknown"),
                "timestamp": datetime.utcnow().isoformat(),
                "confidence": doc.get("confidence", 0.8),
                "verified": doc.get("verified", False)
            }
            
            # Add optional fields if available
            if doc.get("url"):
                provenance["source_url"] = doc["url"]
            if doc.get("domain"):
                provenance["domain"] = doc["domain"]
            if doc.get("trust_score"):
                provenance["trust_score"] = doc["trust_score"]
            
            provenance_list.append(provenance)
        
        # If no sources, add generated content provenance
        if not provenance_list:
            provenance_list.append({
                "source_type": "generated",
                "source_id": "llm_generation",
                "timestamp": datetime.utcnow().isoformat(),
                "confidence": 0.7,
                "verified": False
            })
        
        return provenance_list
    
    async def update_confidence_from_feedback(self, response_id: str, 
                                            feedback_score: float, user_id: str):
        """Update confidence based on user feedback"""
        # Store feedback for future confidence calculations
        feedback_entry = {
            "response_id": response_id,
            "feedback_score": feedback_score,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Log feedback
        await immutable_log.append(
            actor=user_id,
            action="confidence_feedback",
            resource=f"response/{response_id}",
            outcome="success",
            payload=feedback_entry
        )
        
        logger.info(f"Updated confidence feedback for response {response_id}: {feedback_score}")
    
    def get_provenance_stats(self) -> Dict[str, Any]:
        """Get provenance pipeline statistics"""
        return {
            **self.stats,
            "provenance_compliance_rate": (
                (self.stats["responses_processed"] - self.stats["provenance_violations"]) / 
                max(self.stats["responses_processed"], 1)
            ),
            "confidence_weights": self.confidence_weights
        }

# Global instance
provenance_pipeline = ProvenancePipeline()