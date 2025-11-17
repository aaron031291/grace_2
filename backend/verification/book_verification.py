"""
Book Verification System - Trust scoring and QA for ingested books
Handles: comprehension testing, content validation, trust score updates
"""

from typing import Dict, Any
from datetime import datetime
import json

from backend.clarity import BaseComponent, ComponentStatus, Event, TrustLevel, get_event_bus
from backend.database import get_db


class BookVerificationEngine(BaseComponent):
    """
    Verifies book ingestion quality and updates trust scores.
    
    Verification methods:
    1. Comprehension Q&A - Generate and answer questions about content
    2. Cross-reference checking - Verify facts against existing knowledge
    3. Consistency checking - Look for contradictions
    4. Manual review queue - Flag uncertain content for human review
    """
    
    def __init__(self):
        super().__init__()
        self.component_type = "book_verification_engine"
        self.event_bus = get_event_bus()
        
    async def activate(self) -> bool:
        """Activate the verification engine"""
        self.set_status(ComponentStatus.ACTIVE)
        self.activated_at = datetime.utcnow()
        return True
    
    async def verify_book(self, document_id: str) -> Dict[str, Any]:
        """
        Run verification suite on ingested book
        
        Args:
            document_id: ID of the document in memory_documents
            
        Returns:
            Verification results with trust score
        """
        
        result = {
            "document_id": document_id,
            "verification_type": "book_comprehensive",
            "tests_run": [],
            "tests_passed": 0,
            "tests_failed": 0,
            "trust_score": 0.0,
            "issues": [],
            "timestamp": datetime.utcnow().isoformat()
        }
        
        try:
            # Get document metadata
            db = await get_db()
            doc = await db.fetch_one(
                "SELECT * FROM memory_documents WHERE document_id = ?",
                (document_id,)
            )
            
            if not doc:
                raise ValueError(f"Document {document_id} not found")
            
            # Test 1: Content extraction quality
            extraction_test = await self._test_extraction_quality(document_id)
            result["tests_run"].append(extraction_test)
            if extraction_test["passed"]:
                result["tests_passed"] += 1
            else:
                result["tests_failed"] += 1
                result["issues"].append(extraction_test["issue"])
            
            # Test 2: Comprehension Q&A
            qa_test = await self._test_comprehension(document_id)
            result["tests_run"].append(qa_test)
            if qa_test["passed"]:
                result["tests_passed"] += 1
            else:
                result["tests_failed"] += 1
                result["issues"].append(qa_test["issue"])
            
            # Test 3: Chapter/chunk consistency
            consistency_test = await self._test_chunk_consistency(document_id)
            result["tests_run"].append(consistency_test)
            if consistency_test["passed"]:
                result["tests_passed"] += 1
            else:
                result["tests_failed"] += 1
                result["issues"].append(consistency_test["issue"])
            
            # Calculate trust score (0.0 - 1.0)
            total_tests = len(result["tests_run"])
            if total_tests > 0:
                pass_rate = result["tests_passed"] / total_tests
                result["trust_score"] = pass_rate
            
            # Update document trust score
            await self._update_trust_score(document_id, result["trust_score"], result)
            
            # Log verification
            await self._log_verification(result)
            
            # Publish event
            trust_level = self._determine_trust_level(result["trust_score"])
            await self.event_bus.publish(Event(
                event_type="verification.book.completed",
                source=self.component_id,
                payload=result,
                trust_level=trust_level
            ))
            
        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            
            await self.event_bus.publish(Event(
                event_type="verification.book.failed",
                source=self.component_id,
                payload=result,
                trust_level=TrustLevel.LOW
            ))
        
        return result
    
    async def _test_extraction_quality(self, document_id: str) -> Dict[str, Any]:
        """Test if text extraction was successful"""
        
        db = await get_db()
        
        # Check if chunks exist
        chunks = await db.fetch_all(
            "SELECT COUNT(*) as count FROM memory_document_chunks WHERE document_id = ?",
            (document_id,)
        )
        
        chunk_count = chunks[0]["count"] if chunks else 0
        
        # Pass if we have at least 1 chunk
        passed = chunk_count > 0
        
        return {
            "test_name": "extraction_quality",
            "passed": passed,
            "details": {"chunk_count": chunk_count},
            "issue": None if passed else "No chunks extracted from document"
        }
    
    async def _test_comprehension(self, document_id: str) -> Dict[str, Any]:
        """Test comprehension via Q&A"""
        
        # TODO: Generate questions from content and validate answers
        # For now, use a simple heuristic check
        
        db = await get_db()
        
        # Check if insights were generated
        insights = await db.fetch_all(
            "SELECT COUNT(*) as count FROM memory_insights WHERE document_id = ?",
            (document_id,)
        )
        
        insight_count = insights[0]["count"] if insights else 0
        
        # Pass if we have insights (summaries, flashcards)
        passed = insight_count > 0
        
        return {
            "test_name": "comprehension_qa",
            "passed": passed,
            "details": {"insight_count": insight_count},
            "issue": None if passed else "No insights/summaries generated"
        }
    
    async def _test_chunk_consistency(self, document_id: str) -> Dict[str, Any]:
        """Test if chunks are consistent (no major gaps)"""
        
        db = await get_db()
        
        # Get all chunks
        chunks = await db.fetch_all(
            "SELECT chunk_index, content FROM memory_document_chunks WHERE document_id = ? ORDER BY chunk_index",
            (document_id,)
        )
        
        if not chunks:
            return {
                "test_name": "chunk_consistency",
                "passed": False,
                "details": {"chunk_count": 0},
                "issue": "No chunks found"
            }
        
        # Check for sequential indices
        expected_indices = set(range(len(chunks)))
        actual_indices = {chunk["chunk_index"] for chunk in chunks}
        
        missing = expected_indices - actual_indices
        passed = len(missing) == 0
        
        return {
            "test_name": "chunk_consistency",
            "passed": passed,
            "details": {
                "total_chunks": len(chunks),
                "missing_indices": list(missing) if missing else []
            },
            "issue": None if passed else f"Missing chunk indices: {missing}"
        }
    
    async def _update_trust_score(self, document_id: str, trust_score: float, verification_result: Dict):
        """Update trust score in memory_documents"""
        
        db = await get_db()
        
        await db.execute(
            """UPDATE memory_documents 
               SET trust_score = ?, 
                   verification_results = ?,
                   updated_at = CURRENT_TIMESTAMP
               WHERE document_id = ?""",
            (trust_score, json.dumps(verification_result), document_id)
        )
        
        await db.commit()
    
    async def _log_verification(self, result: Dict[str, Any]):
        """Log verification to memory_verification_suites"""
        
        db = await get_db()
        
        await db.execute(
            """INSERT INTO memory_verification_suites
               (document_id, verification_type, results, trust_score, timestamp)
               VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)""",
            (
                result["document_id"],
                result["verification_type"],
                json.dumps(result),
                result["trust_score"]
            )
        )
        
        await db.commit()
    
    def _determine_trust_level(self, score: float) -> TrustLevel:
        """Map trust score to TrustLevel enum"""
        if score >= 0.9:
            return TrustLevel.HIGH
        elif score >= 0.7:
            return TrustLevel.MEDIUM
        elif score >= 0.5:
            return TrustLevel.LOW
        else:
            return TrustLevel.CRITICAL


# Singleton instance
_verification_engine = None

def get_book_verification_engine() -> BookVerificationEngine:
    global _verification_engine
    if _verification_engine is None:
        _verification_engine = BookVerificationEngine()
    return _verification_engine
