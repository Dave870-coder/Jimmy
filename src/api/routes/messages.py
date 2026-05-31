"""API routes for messages."""

import uuid
from datetime import datetime

from fastapi import APIRouter, HTTPException, status

from src.ai.orchestrator import agent_orchestrator
from src.schemas import MessageCreate, MessageResponse

router = APIRouter(prefix="/api/v1/messages", tags=["messages"])


@router.post("/send", response_model=MessageResponse)
async def send_message(message: MessageCreate, user_id: str):
    """Send a message and get AI response."""
    message_id = str(uuid.uuid4())
    
    # Process through AI agent
    response_text = await agent_orchestrator.process(user_id, message.content)
    
    return MessageResponse(
        id=message_id,
        user_id=user_id,
        content=message.content,
        response=response_text,
        ai_model="gpt-4-turbo-preview",
        created_at=datetime.utcnow(),
    )


@router.get("/{user_id}", response_model=list[MessageResponse])
async def get_user_messages(user_id: str, limit: int = 50):
    """Get conversation history for a user."""
    # TODO: Retrieve from database
    return []


@router.get("/{message_id}", response_model=MessageResponse)
async def get_message(message_id: str):
    """Get a specific message."""
    # TODO: Retrieve from database
    raise HTTPException(status_code=404, detail="Message not found")


@router.delete("/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_message(message_id: str):
    """Delete a message."""
    # TODO: Delete from database
    pass
