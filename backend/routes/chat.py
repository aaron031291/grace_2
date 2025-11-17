from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from typing import Optional
from backend.auth import get_current_user
from backend.memory import PersistentMemory
from backend.grace import GraceAutonomous
from backend.causal import causal_tracker
from backend.hunter import hunter
from backend.models import ChatMessage, async_session
router = APIRouter(prefix="/api/chat", tags=["chat"])

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

memory = PersistentMemory()
grace = GraceAutonomous()  # No arguments needed

@router.post("/", response_model=ChatResponse)
async def chat_endpoint(
    req: ChatRequest,
    current_user: str = Depends(get_current_user),
):
    alerts = await hunter.inspect(current_user, "chat_message", req.message, {"content": req.message})
    if alerts:
        print(f"[WARN] Hunter: {len(alerts)} alerts on chat message")

    await memory.store(current_user, "user", req.message)

    async with async_session() as session:
        result = await session.execute(
            select(ChatMessage)
            .where(ChatMessage.user == current_user)
            .order_by(ChatMessage.created_at.desc())
            .limit(1)
        )
        user_msg = result.scalar_one()
        trigger_id = user_msg.id

    result = await grace.respond(current_user, req.message)
    await memory.store(current_user, "grace", result)

    async with async_session() as session:
        result_query = await session.execute(
            select(ChatMessage)
            .where(ChatMessage.user == current_user)
            .order_by(ChatMessage.created_at.desc())
            .limit(1)
        )
        response_msg = result_query.scalar_one()
        response_id = response_msg.id

    await causal_tracker.log_interaction(current_user, trigger_id, response_id)

    return ChatResponse(response=result)


@router.post("/upload")
async def chat_upload(
    file: UploadFile = File(...),
    message: Optional[str] = None,
    current_user: str = Depends(get_current_user),
):
    """
    Upload file attachment for chat
    Ingests the file and returns a reference ID
    """
    try:
        # Read file content
        file_content = await file.read()
        
        # Use ingestion service to process the file
        try:
            from ..ingestion_services.ingestion_service import ingestion_service
            
            artifact_id = await ingestion_service.ingest_file(
                file_content=file_content,
                filename=file.filename,
                actor=current_user
            )
            
            # If there's an accompanying message, process it with context
            response_text = f"File '{file.filename}' uploaded successfully (ID: {artifact_id})"
            
            if message:
                # Store message with file reference
                await memory.store(current_user, "user", f"{message} [Attachment: {file.filename}]")
                
                # Get Grace to respond with file context
                grace_response = await grace.respond(
                    current_user,
                    f"{message}\n\n[User uploaded file: {file.filename}, size: {len(file_content)} bytes, artifact ID: {artifact_id}]"
                )
                
                await memory.store(current_user, "grace", grace_response)
                response_text = grace_response
            
            return {
                "status": "success",
                "artifact_id": artifact_id,
                "filename": file.filename,
                "size": len(file_content),
                "response": response_text,
            }
        except ImportError:
            # Fallback if ingestion service not available
            return {
                "status": "success",
                "artifact_id": None,
                "filename": file.filename,
                "size": len(file_content),
                "response": f"File '{file.filename}' received but ingestion service not available",
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
