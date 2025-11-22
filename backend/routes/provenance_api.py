"""
Provenance API - Endpoints for provenance and citation management
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

from backend.provenance.provenance_pipeline import provenance_pipeline
from backend.api.citation_formatter import citation_formatter
from backend.schemas import DataProvenance

router = APIRouter(prefix="/api/provenance", tags=["Provenance"])

class ProvenanceResponse(BaseModel):
    """Response with full provenance data"""
    response_id: str
    content: str
    confidence_score: float
    data_provenance: List[DataProvenance]
    citations: List[Dict[str, Any]]
    citation_summary: Dict[str, Any]
    provenance_metadata: Dict[str, Any]

class ConfidenceFeedback(BaseModel):
    """User feedback on confidence"""
    response_id: str
    feedback_score: float  # 0-1
    feedback_type: str  # "helpful", "accurate", "relevant"
    comments: Optional[str] = None

@router.get("/stats")
async def get_provenance_stats():
    """Get provenance pipeline statistics"""
    stats = provenance_pipeline.get_provenance_stats()
    
    return {
        "provenance_stats": stats,
        "timestamp": datetime.utcnow().isoformat(),
        "compliance_status": "compliant" if stats["provenance_compliance_rate"] > 0.95 else "needs_attention"
    }

@router.post("/enhance-response")
async def enhance_response_with_provenance(
    response_data: Dict[str, Any],
    source_documents: Optional[List[Dict[str, Any]]] = None
):
    """Enhance response with full provenance and citations"""
    
    # Apply provenance pipeline
    enhanced_response = await provenance_pipeline.enforce_provenance_requirement(
        response_data, source_documents or []
    )
    
    # Format citations for UI
    citations = enhanced_response.get("citations", [])
    citation_ui_data = citation_formatter.format_citations_for_ui(citations, style="web")
    
    # Add inline citation markers
    if "answer" in enhanced_response and citations:
        enhanced_response["answer"] = citation_formatter.create_inline_citation_markers(
            enhanced_response["answer"], citations
        )
    
    return {
        "enhanced_response": enhanced_response,
        "citation_ui_data": citation_ui_data,
        "provenance_summary": {
            "total_sources": len(source_documents or []),
            "confidence_score": enhanced_response.get("confidence_score", 0),
            "verified_sources": sum(1 for doc in (source_documents or []) if doc.get("verified", False)),
            "source_types": list(set(doc.get("source_type", "unknown") for doc in (source_documents or [])))
        }
    }

@router.get("/citations/{response_id}")
async def get_response_citations(
    response_id: str,
    style: str = Query("web", description="Citation style: academic, web, compact, tooltip")
):
    """Get formatted citations for a response"""
    
    # In production, retrieve from database
    # For demo, return mock citations
    mock_citations = [
        {
            "id": "cite_1",
            "source_id": "doc_123",
            "title": "Advanced RAG Techniques",
            "author": "Dr. Jane Smith",
            "url": "https://example.com/rag-techniques",
            "date": "2024-01-15T10:00:00Z",
            "excerpt": "Retrieval-augmented generation combines the power of large language models with external knowledge sources...",
            "confidence": 0.92,
            "verified": True,
            "source_type": "academic"
        },
        {
            "id": "cite_2", 
            "source_id": "web_456",
            "title": "Building Trust in AI Systems",
            "author": "Tech Research Institute",
            "url": "https://example.com/ai-trust",
            "date": "2024-02-20T14:30:00Z",
            "excerpt": "Trust in AI systems requires transparency, explainability, and robust provenance tracking...",
            "confidence": 0.85,
            "verified": False,
            "source_type": "web"
        }
    ]
    
    citation_ui_data = citation_formatter.format_citations_for_ui(mock_citations, style=style)
    citation_summary = citation_formatter.generate_citation_summary(mock_citations)
    
    return {
        "response_id": response_id,
        "citations": citation_ui_data["citations"],
        "citation_map": citation_ui_data["citation_map"],
        "citation_summary": citation_summary,
        "ui_config": citation_ui_data["ui_config"]
    }

@router.post("/feedback")
async def submit_confidence_feedback(feedback: ConfidenceFeedback):
    """Submit user feedback on response confidence"""
    
    await provenance_pipeline.update_confidence_from_feedback(
        response_id=feedback.response_id,
        feedback_score=feedback.feedback_score,
        user_id="current_user"  # Would get from auth context
    )
    
    return {
        "status": "success",
        "message": "Feedback recorded successfully",
        "feedback_id": f"fb_{int(datetime.utcnow().timestamp())}",
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/confidence-analysis/{response_id}")
async def get_confidence_analysis(response_id: str):
    """Get detailed confidence analysis for a response"""
    
    # Mock confidence analysis
    analysis = {
        "response_id": response_id,
        "overall_confidence": 0.87,
        "confidence_factors": {
            "source_reliability": {
                "score": 0.92,
                "weight": 0.3,
                "contribution": 0.276,
                "description": "Sources are highly reliable and well-established"
            },
            "content_freshness": {
                "score": 0.85,
                "weight": 0.2,
                "contribution": 0.17,
                "description": "Content is relatively recent and up-to-date"
            },
            "verification_status": {
                "score": 0.75,
                "weight": 0.25,
                "contribution": 0.1875,
                "description": "75% of sources have been verified"
            },
            "retrieval_accuracy": {
                "score": 0.90,
                "weight": 0.15,
                "contribution": 0.135,
                "description": "High semantic similarity between query and sources"
            },
            "user_feedback": {
                "score": 0.80,
                "weight": 0.1,
                "contribution": 0.08,
                "description": "Positive user feedback on similar responses"
            }
        },
        "recommendations": [
            "Consider verifying additional sources to improve confidence",
            "Monitor user feedback to refine confidence scoring"
        ],
        "confidence_trend": "stable",
        "last_updated": datetime.utcnow().isoformat()
    }
    
    return analysis

@router.get("/source-lineage/{source_id}")
async def get_source_lineage(source_id: str):
    """Get complete lineage for a source"""
    
    # Mock source lineage
    lineage = {
        "source_id": source_id,
        "lineage_chain": [
            {
                "step": 1,
                "actor": "web_scraper",
                "action": "content_extracted",
                "timestamp": "2024-01-15T10:00:00Z",
                "metadata": {"url": "https://example.com/original", "method": "beautifulsoup"}
            },
            {
                "step": 2,
                "actor": "content_processor",
                "action": "text_cleaned",
                "timestamp": "2024-01-15T10:01:00Z",
                "metadata": {"operations": ["html_removal", "text_normalization"]}
            },
            {
                "step": 3,
                "actor": "embedding_service",
                "action": "vectorized",
                "timestamp": "2024-01-15T10:02:00Z",
                "metadata": {"model": "text-embedding-ada-002", "dimensions": 1536}
            },
            {
                "step": 4,
                "actor": "vector_store",
                "action": "indexed",
                "timestamp": "2024-01-15T10:03:00Z",
                "metadata": {"index": "knowledge_base", "chunk_id": "chunk_789"}
            }
        ],
        "current_status": "active",
        "trust_score": 0.92,
        "verification_history": [
            {
                "verified_at": "2024-01-15T12:00:00Z",
                "verified_by": "hunter_protocol",
                "status": "verified",
                "confidence": 0.95
            }
        ]
    }
    
    return lineage

@router.post("/batch-enhance")
async def batch_enhance_responses(
    responses: List[Dict[str, Any]],
    citation_style: str = "web"
):
    """Batch enhance multiple responses with provenance"""
    
    enhanced_responses = []
    
    for response_data in responses:
        # Apply provenance pipeline
        enhanced_response = await provenance_pipeline.enforce_provenance_requirement(
            response_data, response_data.get("source_documents", [])
        )
        
        # Format citations
        citations = enhanced_response.get("citations", [])
        citation_ui_data = citation_formatter.format_citations_for_ui(citations, style=citation_style)
        
        enhanced_responses.append({
            "original_response": response_data,
            "enhanced_response": enhanced_response,
            "citation_ui_data": citation_ui_data
        })
    
    return {
        "enhanced_responses": enhanced_responses,
        "batch_summary": {
            "total_responses": len(responses),
            "total_citations": sum(len(r["enhanced_response"].get("citations", [])) for r in enhanced_responses),
            "average_confidence": sum(r["enhanced_response"].get("confidence_score", 0) for r in enhanced_responses) / max(len(enhanced_responses), 1)
        }
    }
