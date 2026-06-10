"""API routes for messages."""

import uuid
from datetime import datetime

from fastapi import APIRouter, HTTPException, status

from src.ai.orchestrator import get_agent_orchestrator
from src.schemas import MessageCreate, MessageResponse

router = APIRouter(prefix="/api/v1/messages", tags=["messages"])

# Fallback responses when API key not configured
FALLBACK_RESPONSES = {
    "hello": "Hi there! I'm Jimmy, your AI assistant. How can I help you today?",
    "hi": "Hello! Nice to meet you. What can I do for you?",
    "help": "I can help you with many things! Just ask me anything and I'll do my best to assist.",
    "who": "I'm Jimmy AI Bot, your intelligent digital assistant. I'm here to help with questions and tasks!",
    "what": "I'm an AI chatbot designed to help answer questions and have conversations. What would you like to know?",
}

def get_fallback_response(message: str) -> str:
    """Get a fallback response when API is not available."""
    msg_lower = message.lower().strip()
    
    # Check for keyword matches
    for keyword, response in FALLBACK_RESPONSES.items():
        if keyword in msg_lower:
            return response
    
    # Default fallback response
    if "?" in message:
        return f"That's an interesting question! I'm Jimmy AI Bot. To get full responses, please set your GOOGLE_API_KEY. For now: You asked about '{message.strip()}' - I'm here to help!"
    else:
        return f"I appreciate you saying that! I'm Jimmy AI Bot, ready to have a conversation. Got any questions for me?"


@router.post("/send", response_model=MessageResponse)
async def send_message(message: MessageCreate, user_id: str):
    """Send a message and get AI response."""
    message_id = str(uuid.uuid4())
    
    # Get or create orchestrator
    orchestrator = get_agent_orchestrator()
    
    # Try to use orchestrator if available
    if orchestrator is not None:
        try:
            response_text = await orchestrator.process(user_id, message.content)
            # If we got an error message, use fallback instead
            if "error" in response_text.lower() or "not configured" in response_text.lower():
                response_text = get_fallback_response(message.content)
        except Exception as e:
            response_text = get_fallback_response(message.content)
    else:
        # Use fallback when no orchestrator
        response_text = get_fallback_response(message.content)
    
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
