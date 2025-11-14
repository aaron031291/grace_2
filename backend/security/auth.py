import os
import hashlib
import uuid
from datetime import datetime, timedelta
from typing import Optional, Tuple
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import bcrypt
from .models import User, async_session
from .settings import settings

ALGORITHM = "HS256"

# Fail fast if secret key is missing or weak in production
SECRET_KEY = settings.SECRET_KEY
if not SECRET_KEY or SECRET_KEY == "change-me":
    # In tests/dev it's acceptable, but we still raise to enforce hygiene
    raise RuntimeError("SECRET_KEY is not set. Define it in environment or .env before starting the app.")

ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

security = HTTPBearer()

def is_bcrypt_hash(hashed: str) -> bool:
    return hashed.startswith("$2b$") or hashed.startswith("$2a$") or hashed.startswith("$2y$")

def hash_password(password: str) -> str:
    # bcrypt expects bytes; returns bytes
    salt = bcrypt.gensalt(rounds=settings.BCRYPT_ROUNDS)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Backward compatible verification: support legacy sha256 during transition
    if is_bcrypt_hash(hashed_password):
        try:
            return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
        except ValueError:
            return False
    else:
        # Legacy sha256 check
        return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password

def verify_and_upgrade_password(plain_password: str, user: User) -> bool:
    """Verify user's password; if legacy hash matches, upgrade to bcrypt in DB."""
    if verify_password(plain_password, user.password_hash):
        # If legacy, upgrade
        if not is_bcrypt_hash(user.password_hash):
            new_hash = hash_password(plain_password)
            user.password_hash = new_hash
        return True
    return False

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({
        "exp": expire,
        "jti": str(uuid.uuid4()),
        "type": "access",
        "iat": datetime.utcnow(),
    })
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
        return username
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
