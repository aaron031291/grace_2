"""
Presence API Routes
Multi-user presence tracking
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any

router = APIRouter(prefix="/api/presence", tags=["presence"])


class JoinSessionRequest(BaseModel):
    user_id: str
    user_name: str
    metadata: Optional[Dict[str, Any]] = None


class ViewRequest(BaseModel):
    user_id: str
    file_path: Optional[str] = None
    table_name: Optional[str] = None


class EditRequest(BaseModel):
    user_id: str
    user_name: str
    file_path: Optional[str] = None
    table_name: Optional[str] = None
    row_id: Optional[str] = None


@router.post("/join")
async def join_session(request: JoinSessionRequest):
    """Join workspace session"""
    try:
        from backend.collaboration.presence_system import presence_system
        
        result = await presence_system.join_session(
            request.user_id,
            request.user_name,
            request.metadata
        )
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/heartbeat/{user_id}")
async def send_heartbeat(user_id: str):
    """Send heartbeat"""
    try:
        from backend.collaboration.presence_system import presence_system
        
        result = await presence_system.heartbeat(user_id)
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/view")
async def update_view(request: ViewRequest):
    """Update what user is viewing"""
    try:
        from backend.collaboration.presence_system import presence_system
        
        if request.file_path:
            await presence_system.view_file(request.user_id, request.file_path)
        elif request.table_name:
            await presence_system.view_table(request.user_id, request.table_name)
        
        return {'success': True}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/edit/request")
async def request_edit_permission(request: EditRequest):
    """Request edit permission"""
    try:
        from backend.collaboration.presence_system import presence_system
        
        if request.file_path:
            result = await presence_system.request_edit(
                request.user_id,
                request.user_name,
                request.file_path
            )
        elif request.table_name and request.row_id:
            result = await presence_system.request_edit_row(
                request.user_id,
                request.table_name,
                request.row_id
            )
        else:
            raise HTTPException(status_code=400, detail="Must specify file_path or table+row")
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/edit/release")
async def release_edit_permission(request: EditRequest):
    """Release edit permission"""
    try:
        from backend.collaboration.presence_system import presence_system
        
        if request.file_path:
            result = await presence_system.release_edit(request.user_id, request.file_path)
        elif request.table_name and request.row_id:
            result = await presence_system.release_edit_row(
                request.user_id,
                request.table_name,
                request.row_id
            )
        else:
            raise HTTPException(status_code=400, detail="Must specify file_path or table+row")
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/file/{file_path:path}")
async def get_file_presence(file_path: str):
    """Get presence info for a file"""
    try:
        from backend.collaboration.presence_system import presence_system
        
        presence_info = await presence_system.get_file_presence(file_path)
        return presence_info
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/all")
async def get_all_presence():
    """Get overall presence information"""
    try:
        from backend.collaboration.presence_system import presence_system
        
        presence_info = await presence_system.get_all_presence()
        return presence_info
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
