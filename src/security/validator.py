"""Security utilities for SQL injection prevention and input validation."""

import re
import logging
from typing import Any, List, Optional
from sqlalchemy import text
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)

# SQL injection patterns to detect
DANGEROUS_PATTERNS = [
    r"(?i)(union|select|insert|update|delete|drop|create|alter|exec|script|javascript)",
    r"(?i)(-{2}|/\*|\*/|xp_|sp_)",
    r"(?i)(;|\'|\"|\||&&|\|\||<|>)",
]


class SecurityValidator:
    """Validate input for security threats."""
    
    @staticmethod
    def sanitize_input(value: str, max_length: int = 10000) -> str:
        """
        Sanitize user input to prevent injection attacks.
        
        Args:
            value: Input string to sanitize
            max_length: Maximum allowed length
            
        Returns:
            Sanitized string
            
        Raises:
            HTTPException: If input contains dangerous patterns
        """
        if not isinstance(value, str):
            raise ValueError("Input must be a string")
        
        # Check length
        if len(value) > max_length:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Input too long (max {max_length} characters)"
            )
        
        # Check for dangerous patterns
        for pattern in DANGEROUS_PATTERNS:
            if re.search(pattern, value):
                logger.warning(f"Dangerous pattern detected in input: {pattern}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Input contains invalid characters or patterns"
                )
        
        # Remove leading/trailing whitespace
        value = value.strip()
        
        # Escape single quotes
        value = value.replace("'", "''")
        
        return value
    
    @staticmethod
    def validate_token(token: str) -> bool:
        """
        Validate Telegram bot token format.
        
        Args:
            token: Bot token to validate
            
        Returns:
            True if valid format
        """
        # Telegram tokens are typically: number:alphanumeric_with_dash
        pattern = r'^\d+:[A-Za-z0-9_-]+$'
        if not re.match(pattern, token):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Telegram token format"
            )
        return True
    
    @staticmethod
    def validate_api_key(api_key: str) -> bool:
        """
        Validate Google API key format.
        
        Args:
            api_key: API key to validate
            
        Returns:
            True if valid format
        """
        # Google API keys are typically 39 characters
        if not api_key or len(api_key) < 20:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid API key format"
            )
        return True
    
    @staticmethod
    def build_safe_query(base_query: str, params: dict) -> tuple:
        """
        Build a safe SQL query using parameterized statements.
        
        Args:
            base_query: SQL query with :param placeholders
            params: Dictionary of parameter values
            
        Returns:
            Tuple of (text object, params dict)
        """
        # All parameters are automatically parameterized by SQLAlchemy
        return text(base_query), params
    
    @staticmethod
    def rate_limit_check(user_id: str, max_requests: int = 100) -> bool:
        """
        Simple rate limiting check.
        
        Args:
            user_id: User identifier
            max_requests: Max requests allowed per minute
            
        Returns:
            True if within rate limit
        """
        # This would typically use Redis or a database
        # For now, this is a placeholder for rate limit implementation
        logger.info(f"Rate limit check for user: {user_id}, limit: {max_requests}/min")
        return True


class TokenCounter:
    """Count and manage conversation tokens for large context windows."""
    
    MAX_TOKENS = 7_000_000  # 7 million tokens
    TOKENS_PER_MESSAGE = 50  # Approximate tokens per message
    
    @staticmethod
    def estimate_tokens(text: str) -> int:
        """
        Estimate token count for text (rough approximation).
        
        Args:
            text: Text to count tokens for
            
        Returns:
            Estimated token count
        """
        # Rough estimation: ~4 characters per token
        return len(text) // 4
    
    @staticmethod
    def can_add_message(current_tokens: int, message_text: str) -> bool:
        """
        Check if new message can fit within token limit.
        
        Args:
            current_tokens: Current token count
            message_text: New message text
            
        Returns:
            True if message can fit
        """
        message_tokens = TokenCounter.estimate_tokens(message_text)
        return (current_tokens + message_tokens) <= TokenCounter.MAX_TOKENS
    
    @staticmethod
    def trim_conversation(messages: List[dict], max_tokens: int = 7_000_000) -> List[dict]:
        """
        Trim conversation history to fit within token limit.
        
        Args:
            messages: List of message dictionaries
            max_tokens: Maximum allowed tokens
            
        Returns:
            Trimmed message list
        """
        total_tokens = 0
        trimmed = []
        
        # Process messages in reverse to keep most recent
        for message in reversed(messages):
            msg_tokens = TokenCounter.estimate_tokens(message.get('content', ''))
            if total_tokens + msg_tokens <= max_tokens:
                trimmed.append(message)
                total_tokens += msg_tokens
            else:
                logger.warning(f"Trimming conversation: exceeded {max_tokens} tokens")
                break
        
        return list(reversed(trimmed))


class XSSProtection:
    """Prevent XSS (Cross-Site Scripting) attacks."""
    
    DANGEROUS_TAGS = ['script', 'iframe', 'object', 'embed', 'link', 'style']
    DANGEROUS_ATTRS = ['onclick', 'onload', 'onerror', 'onmouseover']
    
    @staticmethod
    def sanitize_html(content: str) -> str:
        """
        Sanitize HTML content to prevent XSS.
        
        Args:
            content: HTML content to sanitize
            
        Returns:
            Sanitized content
        """
        # Remove dangerous tags
        for tag in XSSProtection.DANGEROUS_TAGS:
            pattern = f"(?i)<{tag}[^>]*>.*?</{tag}>"
            content = re.sub(pattern, '', content)
        
        # Remove dangerous attributes
        for attr in XSSProtection.DANGEROUS_ATTRS:
            pattern = f"(?i){attr}\\s*=\\s*['\"]?[^'\"\\s>]*['\"]?"
            content = re.sub(pattern, '', content)
        
        return content


def validate_message_input(content: str, max_length: int = 10000) -> str:
    """
    Main validation function for message input.
    
    Args:
        content: Message content
        max_length: Max allowed length
        
    Returns:
        Validated and sanitized content
        
    Raises:
        HTTPException: If validation fails
    """
    if not content or not content.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message cannot be empty"
        )
    
    # Sanitize input
    sanitized = SecurityValidator.sanitize_input(content, max_length)
    
    # Protect from XSS
    sanitized = XSSProtection.sanitize_html(sanitized)
    
    return sanitized
