"""
Collaboration API Routes
Multi-user tracking, workflows, and real-time collaboration
"""
from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import logging
import uuid

from backend.auth import get_current_user
from backend.collaboration.presence_system import presence_system
from backend.collaboration.grace_copilot_engine import grace_copilot
from backend.collaboration.workflow_engine import workflow_engine, WorkflowType
from backend.collaboration.websocket_manager import collaboration_ws_manager
from backend.collaboration.notification_service import notification_service
from backend.collaboration.automation_engine import automation_engine, TriggerType

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/collaboration", tags=["collaboration"])


class JoinSessionRequest(BaseModel):
    user_name: str
    metadata: Optional[Dict[str, Any]] = {}


class ViewFileRequest(BaseModel):
    file_path: str


class ViewTableRequest(BaseModel):
    table_name: str


class RequestEditRequest(BaseModel):
    file_path: str


class ReleaseEditRequest(BaseModel):
    file_path: str


class CreateWorkflowRequest(BaseModel):
    workflow_type: str
    title: str
    description: str
    reviewers: List[str] = []
    checklist: List[str] = []


class ApproveWorkflowRequest(BaseModel):
    comments: Optional[str] = ""


class RejectWorkflowRequest(BaseModel):
    reason: str


class UpdateChecklistRequest(BaseModel):
    item_index: int
    completed: bool


class AddCommentRequest(BaseModel):
    comment: str


class CopilotChatRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None


@router.post("/presence/join")
async def join_session(
    request: JoinSessionRequest,
    current_user: dict = Depends(get_current_user)
):
    """Join collaboration session"""
    try:
        result = await presence_system.join_session(
            user_id=current_user["user_id"],
            user_name=request.user_name,
            metadata=request.metadata
        )
        return result
    except Exception as e:
        logger.error(f"Failed to join session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/presence/heartbeat")
async def heartbeat(current_user: dict = Depends(get_current_user)):
    """Send heartbeat to maintain presence"""
    try:
        result = await presence_system.heartbeat(current_user["user_id"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/presence/view-file")
async def view_file(
    request: ViewFileRequest,
    current_user: dict = Depends(get_current_user)
):
    """Notify that user is viewing a file"""
    try:
        await presence_system.view_file(
            user_id=current_user["user_id"],
            file_path=request.file_path
        )
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/presence/view-table")
async def view_table(
    request: ViewTableRequest,
    current_user: dict = Depends(get_current_user)
):
    """Notify that user is viewing a table"""
    try:
        await presence_system.view_table(
            user_id=current_user["user_id"],
            table_name=request.table_name
        )
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/presence/request-edit")
async def request_edit(
    request: RequestEditRequest,
    current_user: dict = Depends(get_current_user)
):
    """Request edit permission for a file"""
    try:
        result = await presence_system.request_edit(
            user_id=current_user["user_id"],
            user_name=current_user.get("username", "Unknown"),
            file_path=request.file_path
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/presence/release-edit")
async def release_edit(
    request: ReleaseEditRequest,
    current_user: dict = Depends(get_current_user)
):
    """Release edit lock on a file"""
    try:
        result = await presence_system.release_edit(
            user_id=current_user["user_id"],
            file_path=request.file_path
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/presence/all")
async def get_all_presence(current_user: dict = Depends(get_current_user)):
    """Get all current presence information"""
    try:
        result = await presence_system.get_all_presence()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/presence/file/{file_path:path}")
async def get_file_presence(
    file_path: str,
    current_user: dict = Depends(get_current_user)
):
    """Get presence info for specific file"""
    try:
        result = await presence_system.get_file_presence(file_path)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/workflows")
async def create_workflow(
    request: CreateWorkflowRequest,
    current_user: dict = Depends(get_current_user)
):
    """Create a new collaboration workflow"""
    try:
        workflow = await workflow_engine.create_workflow(
            workflow_type=WorkflowType(request.workflow_type),
            title=request.title,
            description=request.description,
            created_by=current_user["user_id"],
            reviewers=request.reviewers,
            checklist=request.checklist
        )
        return workflow.to_dict()
    except Exception as e:
        logger.error(f"Failed to create workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/workflows/{workflow_id}/approve")
async def approve_workflow(
    workflow_id: str,
    request: ApproveWorkflowRequest,
    current_user: dict = Depends(get_current_user)
):
    """Approve a workflow"""
    try:
        result = await workflow_engine.approve_workflow(
            workflow_id=workflow_id,
            user_id=current_user["user_id"],
            user_name=current_user.get("username", "Unknown"),
            comments=request.comments
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/workflows/{workflow_id}/reject")
async def reject_workflow(
    workflow_id: str,
    request: RejectWorkflowRequest,
    current_user: dict = Depends(get_current_user)
):
    """Reject a workflow"""
    try:
        result = await workflow_engine.reject_workflow(
            workflow_id=workflow_id,
            user_id=current_user["user_id"],
            user_name=current_user.get("username", "Unknown"),
            reason=request.reason
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/workflows/{workflow_id}/checklist")
async def update_checklist(
    workflow_id: str,
    request: UpdateChecklistRequest,
    current_user: dict = Depends(get_current_user)
):
    """Update workflow checklist item"""
    try:
        result = await workflow_engine.update_checklist(
            workflow_id=workflow_id,
            item_index=request.item_index,
            completed=request.completed,
            user_id=current_user["user_id"]
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/workflows/{workflow_id}/comment")
async def add_comment(
    workflow_id: str,
    request: AddCommentRequest,
    current_user: dict = Depends(get_current_user)
):
    """Add comment to workflow"""
    try:
        result = await workflow_engine.add_comment(
            workflow_id=workflow_id,
            user_id=current_user["user_id"],
            user_name=current_user.get("username", "Unknown"),
            comment=request.comment
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workflows/{workflow_id}")
async def get_workflow(
    workflow_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get workflow details"""
    try:
        workflow = await workflow_engine.get_workflow(workflow_id)
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        return workflow
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workflows")
async def get_workflows(
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get workflows (optionally filtered by status)"""
    try:
        if status == "pending":
            workflows = await workflow_engine.get_pending_workflows()
        else:
            workflows = await workflow_engine.get_user_workflows(current_user["user_id"])
        return workflows
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/copilot/chat")
async def copilot_chat(
    request: CopilotChatRequest,
    current_user: dict = Depends(get_current_user)
):
    """Chat with Grace co-pilot"""
    try:
        if not grace_copilot._initialized:
            await grace_copilot.initialize()
        
        result = await grace_copilot.chat(
            user_id=current_user["user_id"],
            message=request.message,
            context=request.context
        )
        return result
    except Exception as e:
        logger.error(f"Copilot chat failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/copilot/suggest-schema")
async def suggest_schema(
    file_path: str,
    file_content: str,
    current_user: dict = Depends(get_current_user)
):
    """Get AI schema suggestion"""
    try:
        result = await grace_copilot.suggest_schema(file_path, file_content)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/copilot/explain-file")
async def explain_file(
    file_path: str,
    file_content: str,
    current_user: dict = Depends(get_current_user)
):
    """Get AI explanation of file"""
    try:
        result = await grace_copilot.explain_file(
            file_path=file_path,
            file_content=file_content,
            user_id=current_user["user_id"]
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.websocket("/ws")
async def collaboration_websocket(websocket: WebSocket, token: str):
    """WebSocket endpoint for real-time collaboration"""
    session_id = str(uuid.uuid4())
    user_id = None
    
    try:
        from backend.auth import verify_token
        user_data = verify_token(token)
        if not user_data:
            await websocket.close(code=1008, reason="Invalid token")
            return
        
        user_id = user_data.get("user_id", "unknown")
        
        await collaboration_ws_manager.connect(websocket, user_id, session_id)
        
        while True:
            try:
                data = await websocket.receive_json()
                await collaboration_ws_manager.handle_message(session_id, data)
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Error handling WebSocket message: {e}")
                break
    
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
    
    finally:
        collaboration_ws_manager.disconnect(session_id)
        if user_id:
            await presence_system.remove_user(user_id)


@router.get("/notifications")
async def get_notifications(
    unread_only: bool = False,
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    """Get user notifications"""
    try:
        notifications = await notification_service.get_user_notifications(
            user_id=current_user["user_id"],
            unread_only=unread_only,
            limit=limit
        )
        return {"notifications": notifications}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/notifications/unread-count")
async def get_unread_count(current_user: dict = Depends(get_current_user)):
    """Get unread notification count"""
    try:
        count = await notification_service.get_unread_count(current_user["user_id"])
        return {"count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Mark notification as read"""
    try:
        success = await notification_service.mark_read(notification_id, current_user["user_id"])
        return {"success": success}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/notifications/mark-all-read")
async def mark_all_read(current_user: dict = Depends(get_current_user)):
    """Mark all notifications as read"""
    try:
        await notification_service.mark_all_read(current_user["user_id"])
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/notifications/{notification_id}/dismiss")
async def dismiss_notification(
    notification_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Dismiss notification"""
    try:
        success = await notification_service.dismiss(notification_id, current_user["user_id"])
        return {"success": success}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class CreateAutomationRuleRequest(BaseModel):
    name: str
    description: str
    trigger_type: str
    trigger_conditions: Dict[str, Any]
    actions: List[Dict[str, Any]]


@router.post("/automation/rules")
async def create_automation_rule(
    request: CreateAutomationRuleRequest,
    current_user: dict = Depends(get_current_user)
):
    """Create automation rule"""
    try:
        rule = await automation_engine.create_rule(
            name=request.name,
            description=request.description,
            trigger_type=TriggerType(request.trigger_type),
            trigger_conditions=request.trigger_conditions,
            actions=request.actions
        )
        return rule.to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/automation/rules")
async def list_automation_rules(current_user: dict = Depends(get_current_user)):
    """List all automation rules"""
    try:
        rules = await automation_engine.list_rules()
        return {"rules": rules}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/automation/rules/{rule_id}")
async def get_automation_rule(
    rule_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get automation rule"""
    try:
        rule = await automation_engine.get_rule(rule_id)
        if not rule:
            raise HTTPException(status_code=404, detail="Rule not found")
        return rule
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/automation/rules/{rule_id}/enable")
async def enable_automation_rule(
    rule_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Enable automation rule"""
    try:
        await automation_engine.enable_rule(rule_id)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/automation/rules/{rule_id}/disable")
async def disable_automation_rule(
    rule_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Disable automation rule"""
    try:
        await automation_engine.disable_rule(rule_id)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/automation/rules/{rule_id}")
async def delete_automation_rule(
    rule_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete automation rule"""
    try:
        await automation_engine.delete_rule(rule_id)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
