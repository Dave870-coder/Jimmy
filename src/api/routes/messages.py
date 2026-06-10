"""API routes for messages."""

import uuid
from datetime import datetime

from fastapi import APIRouter, HTTPException, status

from src.ai.orchestrator import get_agent_orchestrator
from src.schemas import MessageCreate, MessageResponse
from src.security.validator import validate_message_input, TokenCounter

router = APIRouter(prefix="/api/v1/messages", tags=["messages"])

# Conversation history storage (in production, use database)
conversation_history = {}

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
        return f"That's an interesting question! I'm Jimmy AI Bot. To get full responses, please configure Google API Key in Settings. For now: You asked about '{message.strip()}' - I'm here to help!"
    else:
        return f"I appreciate you saying that! I'm Jimmy AI Bot, ready to have a conversation. Got any questions for me?"


@router.post("/send", response_model=MessageResponse)
async def send_message(message: MessageCreate, user_id: str):
    """
    Send a message and get AI response.
    
    Supports:
    - Up to 7 million tokens in conversation history
    - Complex multi-turn conversations
    - SQL injection protection
    - Input validation and sanitization
    """
    message_id = str(uuid.uuid4())
    
    # Validate and sanitize input
    try:
        validated_content = validate_message_input(message.content)
    except HTTPException as e:
        raise e
    
    # Initialize conversation history for user if needed
    if user_id not in conversation_history:
        conversation_history[user_id] = {
            'messages': [],
            'total_tokens': 0,
        }
    
    user_conv = conversation_history[user_id]
    
    # Check if message fits within token limit
    if not TokenCounter.can_add_message(user_conv['total_tokens'], validated_content):
        # Trim old messages to make room
        user_conv['messages'] = TokenCounter.trim_conversation(user_conv['messages'])
        user_conv['total_tokens'] = sum(
            TokenCounter.estimate_tokens(msg.get('content', ''))
            for msg in user_conv['messages']
        )
    
    # Get or create orchestrator
    orchestrator = get_agent_orchestrator()
    
    # Try to use orchestrator if available
    if orchestrator is not None:
        try:
            response_text = await orchestrator.process(user_id, validated_content)
            # If we got an error message, use fallback instead
            if "error" in response_text.lower() or "not configured" in response_text.lower():
                response_text = get_fallback_response(validated_content)
        except Exception as e:
            response_text = get_fallback_response(validated_content)
    else:
        # Use fallback when no orchestrator
        response_text = get_fallback_response(validated_content)
    
    # Add messages to conversation history
    user_conv['messages'].append({
        'id': message_id,
        'role': 'user',
        'content': validated_content,
        'timestamp': datetime.utcnow().isoformat(),
    })
    
    response_message_id = str(uuid.uuid4())
    user_conv['messages'].append({
        'id': response_message_id,
        'role': 'assistant',
        'content': response_text,
        'timestamp': datetime.utcnow().isoformat(),
    })
    
    # Update token count
    user_conv['total_tokens'] += TokenCounter.estimate_tokens(validated_content)
    user_conv['total_tokens'] += TokenCounter.estimate_tokens(response_text)
    
    return MessageResponse(
        id=message_id,
        user_id=user_id,
        content=validated_content,
        response=response_text,
        ai_model="gpt-4-turbo-preview",
        created_at=datetime.utcnow(),
    )


@router.get("/{user_id}", response_model=list[MessageResponse])
async def get_user_messages(user_id: str, limit: int = 50):
    """
    Get conversation history for a user.
    
    Returns:
        List of messages up to limit
    """
    if user_id not in conversation_history:
        return []
    
    messages = conversation_history[user_id]['messages']
    # Return most recent messages up to limit
    return [
        MessageResponse(
            id=msg['id'],
            user_id=user_id,
            content=msg['content'],
            response=msg['content'] if msg['role'] == 'assistant' else '',
            ai_model="gpt-4-turbo-preview",
            created_at=datetime.fromisoformat(msg['timestamp']),
        )
        for msg in messages[-limit:]
    ]


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


@router.get("/stats/{user_id}")
async def get_conversation_stats(user_id: str):
    """Get conversation statistics including token usage."""
    if user_id not in conversation_history:
        return {
            'user_id': user_id,
            'total_messages': 0,
            'total_tokens': 0,
            'tokens_used_percent': 0,
            'can_add_message': True,
        }
    
    user_conv = conversation_history[user_id]
    tokens_percent = (user_conv['total_tokens'] / TokenCounter.MAX_TOKENS) * 100
    
    return {
        'user_id': user_id,
        'total_messages': len(user_conv['messages']),
        'total_tokens': user_conv['total_tokens'],
        'max_tokens': TokenCounter.MAX_TOKENS,
        'tokens_used_percent': tokens_percent,
        'can_add_message': user_conv['total_tokens'] < TokenCounter.MAX_TOKENS,
    }

    
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
