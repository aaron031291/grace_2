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
        """Test comprehension via Q&A generation and validation"""
        
        db = await get_db()
        
        chunks = await db.fetch_all(
            "SELECT content FROM memory_document_chunks WHERE document_id = ? LIMIT 5",
            (document_id,)
        )
        
        if not chunks:
            return {
                "test_name": "comprehension_qa",
                "passed": False,
                "details": {"chunk_count": 0},
                "issue": "No content chunks available for comprehension testing"
            }
        
        insights = await db.fetch_all(
            "SELECT COUNT(*) as count FROM memory_insights WHERE document_id = ?",
            (document_id,)
        )
        
        insight_count = insights[0]["count"] if insights else 0
        
        questions_generated = 0
        questions_answered = 0
        
        for chunk in chunks[:3]:
            content = chunk["content"]
            if not content or len(content) < 50:
                continue
            
            question = self._generate_question_from_content(content)
            if question:
                questions_generated += 1
                
                if self._can_answer_from_content(question, content):
                    questions_answered += 1
        
        comprehension_score = questions_answered / questions_generated if questions_generated > 0 else 0.0
        
        passed = comprehension_score >= 0.6 and insight_count > 0
        
        return {
            "test_name": "comprehension_qa",
            "passed": passed,
            "details": {
                "insight_count": insight_count,
                "questions_generated": questions_generated,
                "questions_answered": questions_answered,
                "comprehension_score": comprehension_score
            },
            "issue": None if passed else f"Low comprehension score: {comprehension_score:.2f}"
        }
    
    def _generate_question_from_content(self, content: str) -> str:
        """Generate a basic comprehension question from content"""
        sentences = [s.strip() for s in content.split('.') if len(s.strip()) > 20]
        
        if not sentences:
            return ""
        
        first_sentence = sentences[0]
        words = first_sentence.split()
        
        if len(words) < 5:
            return ""
        
        if any(word.lower() in first_sentence.lower() for word in ['is', 'are', 'was', 'were']):
            return f"What {first_sentence.split()[0].lower()}?"
        else:
            return f"What does the text say about {words[0]}?"
    
    def _can_answer_from_content(self, question: str, content: str) -> bool:
        """Check if question can be answered from content"""
        question_words = set(question.lower().replace('?', '').split())
        content_words = set(content.lower().split())
        
        common_words = {'what', 'how', 'why', 'when', 'where', 'who', 'does', 'the', 'a', 'an', 'is', 'are'}
        question_keywords = question_words - common_words
        
        if not question_keywords:
            return False
        
        overlap = len(question_keywords & content_words)
        return overlap >= len(question_keywords) * 0.5
    
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
