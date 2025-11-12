"""
Collaboration Workflow Engine
Manages approval pipelines, checklists, and review workflows
"""
import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
import uuid

logger = logging.getLogger(__name__)


class WorkflowType(str, Enum):
    SCHEMA_APPROVAL = "schema_approval"
    INGESTION_RUN = "ingestion_run"
    QUALITY_REVIEW = "quality_review"
    MEMORY_FUSION_SYNC = "memory_fusion_sync"


class WorkflowStatus(str, Enum):
    PENDING = "pending"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"


class Workflow:
    """Represents a collaboration workflow"""
    
    def __init__(
        self,
        workflow_id: str,
        workflow_type: WorkflowType,
        title: str,
        description: str,
        created_by: str,
        reviewers: List[str] = None,
        checklist: List[str] = None
    ):
        self.workflow_id = workflow_id
        self.workflow_type = workflow_type
        self.title = title
        self.description = description
        self.created_by = created_by
        self.reviewers = reviewers or []
        self.checklist = checklist or []
        
        self.status = WorkflowStatus.PENDING
        self.created_at = datetime.utcnow()
        self.completed_at: Optional[datetime] = None
        
        # Checklist state
        self.checklist_completed: List[bool] = [False] * len(self.checklist)
        
        # Approvals
        self.approvals: Dict[str, Dict[str, Any]] = {}
        self.rejections: Dict[str, Dict[str, Any]] = {}
        
        # Comments
        self.comments: List[Dict[str, Any]] = []
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'workflow_id': self.workflow_id,
            'workflow_type': self.workflow_type.value,
            'title': self.title,
            'description': self.description,
            'created_by': self.created_by,
            'reviewers': self.reviewers,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'checklist': [
                {
                    'item': item,
                    'completed': self.checklist_completed[idx]
                }
                for idx, item in enumerate(self.checklist)
            ],
            'approvals': self.approvals,
            'rejections': self.rejections,
            'comments': self.comments,
            'approval_count': len(self.approvals),
            'rejection_count': len(self.rejections),
            'checklist_progress': sum(self.checklist_completed) / len(self.checklist) if self.checklist else 1.0
        }


class WorkflowEngine:
    """
    Manages collaboration workflows.
    Handles approval pipelines, checklists, reviews, and notifications.
    """
    
    def __init__(self):
        self.workflows: Dict[str, Workflow] = {}
        self.user_assignments: Dict[str, List[str]] = {}  # user_id -> workflow_ids
    
    async def create_workflow(
        self,
        workflow_type: WorkflowType,
        title: str,
        description: str,
        created_by: str,
        reviewers: List[str] = None,
        checklist: List[str] = None
    ) -> Workflow:
        """Create a new workflow"""
        workflow_id = str(uuid.uuid4())
        
        workflow = Workflow(
            workflow_id=workflow_id,
            workflow_type=workflow_type,
            title=title,
            description=description,
            created_by=created_by,
            reviewers=reviewers,
            checklist=checklist
        )
        
        self.workflows[workflow_id] = workflow
        
        # Assign to reviewers
        for reviewer in (reviewers or []):
            if reviewer not in self.user_assignments:
                self.user_assignments[reviewer] = []
            self.user_assignments[reviewer].append(workflow_id)
        
        logger.info(f"📋 Workflow created: {title} ({workflow_id})")
        
        # Emit notification
        await self._notify_reviewers(workflow)
        
        return workflow
    
    async def approve_workflow(
        self,
        workflow_id: str,
        user_id: str,
        user_name: str,
        comments: str = ""
    ) -> Dict[str, Any]:
        """Approve a workflow"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return {'success': False, 'error': 'Workflow not found'}
        
        # Record approval
        workflow.approvals[user_id] = {
            'user_id': user_id,
            'user_name': user_name,
            'approved_at': datetime.utcnow().isoformat(),
            'comments': comments
        }
        
        # Check if all reviewers approved
        if len(workflow.approvals) >= len(workflow.reviewers):
            workflow.status = WorkflowStatus.APPROVED
            workflow.completed_at = datetime.utcnow()
            
            logger.info(f"✅ Workflow approved: {workflow.title}")
            
            # Execute workflow
            await self._execute_workflow(workflow)
        else:
            workflow.status = WorkflowStatus.IN_REVIEW
        
        return {
            'success': True,
            'workflow_id': workflow_id,
            'status': workflow.status.value,
            'approval_count': len(workflow.approvals),
            'required_approvals': len(workflow.reviewers)
        }
    
    async def reject_workflow(
        self,
        workflow_id: str,
        user_id: str,
        user_name: str,
        reason: str
    ) -> Dict[str, Any]:
        """Reject a workflow"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return {'success': False, 'error': 'Workflow not found'}
        
        workflow.rejections[user_id] = {
            'user_id': user_id,
            'user_name': user_name,
            'rejected_at': datetime.utcnow().isoformat(),
            'reason': reason
        }
        
        workflow.status = WorkflowStatus.REJECTED
        workflow.completed_at = datetime.utcnow()
        
        logger.info(f"❌ Workflow rejected: {workflow.title} by {user_name}")
        
        return {
            'success': True,
            'workflow_id': workflow_id,
            'status': workflow.status.value
        }
    
    async def update_checklist(
        self,
        workflow_id: str,
        item_index: int,
        completed: bool,
        user_id: str
    ) -> Dict[str, Any]:
        """Update checklist item"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return {'success': False, 'error': 'Workflow not found'}
        
        if item_index >= len(workflow.checklist):
            return {'success': False, 'error': 'Invalid checklist item'}
        
        workflow.checklist_completed[item_index] = completed
        
        # Check if all completed
        all_complete = all(workflow.checklist_completed)
        
        return {
            'success': True,
            'workflow_id': workflow_id,
            'item_index': item_index,
            'completed': completed,
            'all_completed': all_complete,
            'progress': sum(workflow.checklist_completed) / len(workflow.checklist)
        }
    
    async def add_comment(
        self,
        workflow_id: str,
        user_id: str,
        user_name: str,
        comment: str
    ):
        """Add comment to workflow"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return {'success': False, 'error': 'Workflow not found'}
        
        workflow.comments.append({
            'user_id': user_id,
            'user_name': user_name,
            'comment': comment,
            'timestamp': datetime.utcnow().isoformat()
        })
        
        return {'success': True, 'comment_count': len(workflow.comments)}
    
    async def get_workflow(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get workflow details"""
        workflow = self.workflows.get(workflow_id)
        return workflow.to_dict() if workflow else None
    
    async def get_user_workflows(self, user_id: str) -> List[Dict[str, Any]]:
        """Get workflows assigned to user"""
        workflow_ids = self.user_assignments.get(user_id, [])
        
        workflows = []
        for wf_id in workflow_ids:
            workflow = self.workflows.get(wf_id)
            if workflow:
                workflows.append(workflow.to_dict())
        
        return workflows
    
    async def get_pending_workflows(self) -> List[Dict[str, Any]]:
        """Get all pending workflows"""
        pending = [
            wf.to_dict() for wf in self.workflows.values()
            if wf.status in [WorkflowStatus.PENDING, WorkflowStatus.IN_REVIEW]
        ]
        
        return pending
    
    async def _notify_reviewers(self, workflow: Workflow):
        """Notify reviewers about new workflow"""
        # Would integrate with notification system
        logger.info(f"📧 Notifying {len(workflow.reviewers)} reviewers for {workflow.title}")
    
    async def _execute_workflow(self, workflow: Workflow):
        """Execute approved workflow"""
        logger.info(f"🚀 Executing workflow: {workflow.title}")
        
        # Would trigger actual execution based on workflow type
        # e.g., run ingestion, trigger sync, etc.


# Global instance
workflow_engine = WorkflowEngine()
