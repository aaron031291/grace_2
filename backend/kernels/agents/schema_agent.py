"""
Schema Agent - Proposes and validates schema changes for new content types
Handles: schema inference, validation, unified logic routing
"""

from typing import Dict, Any
from datetime import datetime
import json

from backend.clarity import BaseComponent, ComponentStatus, Event, TrustLevel, get_event_bus
from backend.database import get_db


class SchemaAgent(BaseComponent):
    """
    Analyzes new files and proposes appropriate schema entries.
    Routes proposals through Unified Logic for approval.
    """
    
    def __init__(self):
        super().__init__()
        self.component_type = "schema_agent"
        self.event_bus = get_event_bus()
        self.pending_proposals = {}
        
    async def activate(self) -> bool:
        """Activate the schema agent"""
        self.set_status(ComponentStatus.ACTIVE)
        self.activated_at = datetime.utcnow()
        return True
    
    async def analyze_file(self, file_path: str, file_type: str) -> Dict[str, Any]:
        """
        Analyze a file and determine the appropriate schema/table
        
        Args:
            file_path: Path to the file
            file_type: File extension (e.g., .pdf, .txt, .py)
            
        Returns:
            Schema proposal dict
        """
        
        proposal = {
            "file_path": file_path,
            "file_type": file_type,
            "proposed_table": None,
            "proposed_schema": {},
            "confidence": 0.0,
            "reasoning": []
        }
        
        # Determine target table based on file type and location
        if "books" in file_path and file_type in [".pdf", ".epub"]:
            proposal.update({
                "proposed_table": "memory_documents",
                "proposed_schema": {
                    "source_type": "book",
                    "requires_embedding": True,
                    "requires_chunking": True,
                    "requires_summary": True,
                    "verification_type": "comprehension_qa"
                },
                "confidence": 0.9,
                "reasoning": ["File in books directory", "PDF/EPUB format", "Requires full text processing"]
            })
            
        elif file_type in [".txt", ".md", ".rst"]:
            proposal.update({
                "proposed_table": "memory_documents",
                "proposed_schema": {
                    "source_type": "text_document",
                    "requires_embedding": True,
                    "requires_chunking": True,
                    "verification_type": "content_check"
                },
                "confidence": 0.85,
                "reasoning": ["Text-based format", "Suitable for embedding"]
            })
            
        elif file_type in [".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".cpp"]:
            proposal.update({
                "proposed_table": "memory_documents",
                "proposed_schema": {
                    "source_type": "code",
                    "requires_parsing": True,
                    "requires_embedding": True,
                    "verification_type": "syntax_check"
                },
                "confidence": 0.95,
                "reasoning": ["Source code file", "Requires AST parsing"]
            })
            
        elif file_type in [".mp3", ".wav", ".m4a"]:
            proposal.update({
                "proposed_table": "memory_documents",
                "proposed_schema": {
                    "source_type": "audio",
                    "requires_transcription": True,
                    "requires_embedding": True,
                    "verification_type": "audio_quality_check"
                },
                "confidence": 0.8,
                "reasoning": ["Audio format", "Requires transcription pipeline"]
            })
            
        else:
            proposal.update({
                "proposed_table": "memory_documents",
                "proposed_schema": {
                    "source_type": "generic",
                    "requires_inspection": True
                },
                "confidence": 0.5,
                "reasoning": ["Unknown file type", "Requires manual review"]
            })
        
        # Log the proposal
        await self._log_proposal(proposal)
        
        # Publish event
        await self.event_bus.publish(Event(
            event_type="schema.proposal.created",
            source=self.component_id,
            payload=proposal,
            trust_level=TrustLevel.MEDIUM
        ))
        
        return proposal
    
    async def submit_to_unified_logic(self, proposal: Dict[str, Any]) -> Dict[str, Any]:
        """
        Submit schema proposal to Unified Logic for approval
        
        Args:
            proposal: Schema proposal dict
            
        Returns:
            Approval decision
        """
        
        proposal_id = f"schema_{datetime.utcnow().timestamp()}"
        self.pending_proposals[proposal_id] = proposal
        
        # Auto-approve high confidence proposals
        if proposal["confidence"] >= 0.85:
            decision = {
                "proposal_id": proposal_id,
                "status": "approved",
                "approved_by": "auto_approval",
                "reason": f"High confidence ({proposal['confidence']})",
                "timestamp": datetime.utcnow().isoformat()
            }
        elif proposal["confidence"] >= 0.5:
            decision = {
                "proposal_id": proposal_id,
                "status": "pending_review",
                "reason": f"Medium confidence ({proposal['confidence']}), requires manual review",
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            decision = {
                "proposal_id": proposal_id,
                "status": "flagged",
                "reason": f"Low confidence ({proposal['confidence']}), requires human oversight",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # Log decision
        await self._log_decision(proposal_id, decision)
        
        # Publish event
        await self.event_bus.publish(Event(
            event_type="schema.proposal.decided",
            source=self.component_id,
            payload={
                "proposal_id": proposal_id,
                "decision": decision,
                "proposal": proposal
            },
            trust_level=TrustLevel.HIGH if decision["status"] == "approved" else TrustLevel.MEDIUM
        ))
        
        return decision
    
    async def _log_proposal(self, proposal: Dict[str, Any]):
        """Log schema proposal to memory_librarian_log"""
        
        db = await get_db()
        
        await db.execute(
            """INSERT INTO memory_librarian_log
               (action_type, target_path, details, timestamp)
               VALUES (?, ?, ?, CURRENT_TIMESTAMP)""",
            (
                "schema_proposal",
                proposal["file_path"],
                json.dumps(proposal)
            )
        )
        
        await db.commit()
    
    async def _log_decision(self, proposal_id: str, decision: Dict[str, Any]):
        """Log approval decision"""
        
        db = await get_db()
        
        await db.execute(
            """INSERT INTO memory_librarian_log
               (action_type, target_path, details, timestamp)
               VALUES (?, ?, ?, CURRENT_TIMESTAMP)""",
            (
                "schema_approval",
                proposal_id,
                json.dumps(decision)
            )
        )
        
        await db.commit()


# Singleton instance
_schema_agent = None

def get_schema_agent() -> SchemaAgent:
    global _schema_agent
    if _schema_agent is None:
        _schema_agent = SchemaAgent()
    return _schema_agent
