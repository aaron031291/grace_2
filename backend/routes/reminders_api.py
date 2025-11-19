"""
Reminders API - Create and manage reminders

Endpoints:
- Parse natural language reminders
- Create reminders
- List pending reminders
- Complete/cancel reminders
"""

from typing import Dict, Any, List
from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.reminders.reminder_service import reminder_service

router = APIRouter()


class CreateReminderRequest(BaseModel):
    """Create reminder from natural language"""
    text: str
    user_id: str = "user"


class ReminderResponse(BaseModel):
    """Reminder information"""
    reminder_id: str
    message: str
    trigger_time: str | None
    trigger_event: str | None
    status: str


@router.post("/reminders/create")
async def create_reminder_from_text(req: CreateReminderRequest) -> Dict[str, Any]:
    """
    Create reminder from natural language
    
    Examples:
    - "Remind me tomorrow to review the CRM deploy"
    - "Remind me in 2 hours to check logs"
    - "Remind me every Monday to review metrics"
    - "Remind me when the import finishes"
    """
    reminder_id = await reminder_service.parse_natural_language(
        user_id=req.user_id,
        text=req.text
    )
    
    if not reminder_id:
        raise HTTPException(
            status_code=400,
            detail="Could not parse reminder. Try: 'Remind me tomorrow to...'"
        )
    
    return {
        "success": True,
        "reminder_id": reminder_id,
        "message": "Reminder created"
    }


@router.get("/reminders/pending")
async def get_pending_reminders(user_id: str = "user") -> Dict[str, Any]:
    """Get all pending reminders for user"""
    reminders = reminder_service.get_pending_reminders(user_id)
    
    return {
        "reminders": [
            {
                "reminder_id": r["reminder_id"],
                "message": r["message"],
                "trigger_time": r["trigger_time"],
                "trigger_event": r["trigger_event"],
                "created_at": r["created_at"],
            }
            for r in reminders
        ],
        "total": len(reminders)
    }


@router.post("/reminders/{reminder_id}/complete")
async def complete_reminder(reminder_id: str) -> Dict[str, Any]:
    """Mark reminder as completed"""
    # Implementation would update status in DB
    return {
        "success": True,
        "reminder_id": reminder_id,
        "status": "completed"
    }


@router.delete("/reminders/{reminder_id}")
async def cancel_reminder(reminder_id: str) -> Dict[str, Any]:
    """Cancel a reminder"""
    # Implementation would update status to cancelled
    return {
        "success": True,
        "reminder_id": reminder_id,
        "status": "cancelled"
    }
