"""
Authentication Service for Grace

Provides token-based auth for all input channels:
- HTTP endpoints (API tokens)
- WebSocket connections (token handshake)
- Voice/video streams (session tokens)
"""

import os
import jwt
import secrets
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# JWT configuration
SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

# Security scheme
security = HTTPBearer(auto_error=False)

# In-memory session store (replace with Redis/DB in production)
active_sessions: Dict[str, Dict[str, Any]] = {}


def create_access_token(
    user_id: str,
    data: Optional[Dict[str, Any]] = None,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create JWT access token
    
    Args:
        user_id: User identifier
        data: Additional claims
        expires_delta: Token expiration time
    
    Returns:
        JWT token string
    """
    to_encode = {"sub": user_id}
    if data:
        to_encode.update(data)
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Dict[str, Any]:
    """
    Verify JWT token and extract claims
    
    Args:
        token: JWT token string
    
    Returns:
        Token payload
    
    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Dict[str, Any]:
    """
    Dependency to get current authenticated user
    
    Use in endpoints like:
        async def my_endpoint(user: Dict = Depends(get_current_user)):
            ...
    """
    # Allow bypass in development if auth is disabled
    if os.getenv("DISABLE_AUTH") == "true":
        return {"user_id": "dev_user", "role": "admin", "bypass": True}
    
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    token = credentials.credentials
    payload = verify_token(token)
    
    return {
        "user_id": payload.get("sub"),
        "role": payload.get("role", "user"),
        "token": token
    }


def create_session_token(
    user_id: str,
    session_type: str,
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    """
    Create session token for voice/video streams
    
    Args:
        user_id: User identifier
        session_type: Type of session (voice, video, screen)
        metadata: Additional session metadata
    
    Returns:
        Session token string
    """
    session_id = f"{session_type}_{secrets.token_urlsafe(16)}"
    
    session_data = {
        "session_id": session_id,
        "user_id": user_id,
        "session_type": session_type,
        "created_at": datetime.utcnow().isoformat(),
        "metadata": metadata or {}
    }
    
    active_sessions[session_id] = session_data
    
    return session_id


def verify_session_token(session_token: str) -> Dict[str, Any]:
    """
    Verify session token for streaming connections
    
    Args:
        session_token: Session token string
    
    Returns:
        Session data
    
    Raises:
        HTTPException: If session is invalid
    """
    if session_token not in active_sessions:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session token"
        )
    
    return active_sessions[session_token]


def invalidate_session(session_token: str) -> bool:
    """
    Invalidate a session token
    
    Args:
        session_token: Session token to invalidate
    
    Returns:
        True if session was found and invalidated
    """
    if session_token in active_sessions:
        del active_sessions[session_token]
        return True
    return False


def get_user_sessions(user_id: str) -> list[Dict[str, Any]]:
    """
    Get all active sessions for a user
    
    Args:
        user_id: User identifier
    
    Returns:
        List of session data
    """
    return [
        session for session in active_sessions.values()
        if session.get("user_id") == user_id
    ]


# API key validation (for service-to-service)
def verify_api_key(api_key: str) -> bool:
    """
    Verify API key for service authentication
    
    Args:
        api_key: API key string
    
    Returns:
        True if valid
    """
    valid_keys = os.getenv("GRACE_API_KEYS", "").split(",")
    return api_key in valid_keys if valid_keys != [""] else False
