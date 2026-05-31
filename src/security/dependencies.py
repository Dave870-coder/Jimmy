"""Dependency injection utilities."""

from fastapi import Depends, HTTPException, status
from jose import JWTError

from src.security.auth import verify_token


async def get_current_user(authorization: str = None) -> dict:
    """Get current user from JWT token."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    
    token = authorization[7:]  # Remove "Bearer " prefix
    payload = verify_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    
    return {"user_id": user_id, "token": token}


async def get_admin_user(current_user: dict = Depends(get_current_user)) -> dict:
    """Get current user and verify admin privileges."""
    # TODO: Check database for admin role
    return current_user
