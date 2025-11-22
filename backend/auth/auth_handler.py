"""
Placeholder Authentication Handler for Grace.

This provides a dummy `get_current_user` dependency to allow other
modules to load. In a real application, this would be replaced with a
proper authentication system (e.g., OAuth2 with JWTs).
"""

from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt

SECRET_KEY = "a_very_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_and_upgrade_password(plain_password, hashed_password):
    return pwd_context.verify_and_update(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user() -> dict:
    """
    A placeholder dependency that returns a mock user.
    This allows endpoints protected by authentication to run during development
    without a full auth implementation.
    """
    return {
        "username": "grace_agent",
        "email": "grace@system.local",
        "roles": ["admin", "system", "agent"],
    }
